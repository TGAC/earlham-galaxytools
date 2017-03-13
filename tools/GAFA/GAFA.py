from __future__ import print_function

import collections
import optparse
import re
import shutil
import sqlite3

version = "0.3.0"

Sequence = collections.namedtuple('Sequence', ['header', 'sequence'])


def FASTAReader_gen(fasta_filename):
    with open(fasta_filename) as fasta_file:
        line = fasta_file.readline()
        while True:
            if not line:
                return
            assert line.startswith('>'), "FASTA headers must start with >"
            header = line.rstrip()
            sequence_parts = []
            line = fasta_file.readline()
            while line and line[0] != '>':
                sequence_parts.append(line.rstrip())
                line = fasta_file.readline()
            sequence = "".join(sequence_parts)
            yield Sequence(header, sequence)


FASTA_MATCH_RE = re.compile(r'[^-]')


def fasta_aln2cigar(sequence):
    # Converts each match into M and each gap into D
    tmp_seq = FASTA_MATCH_RE.sub('M', sequence)
    tmp_seq = tmp_seq.replace('-', 'D')
    # Split the sequence in substrings composed by the same letter
    tmp_seq = tmp_seq.replace('DM', 'D,M')
    tmp_seq = tmp_seq.replace('MD', 'M,D')
    cigar_list = tmp_seq.split(',')
    # Condense each substring, e.g. DDDD in 4D, and concatenate them again
    cigar = ''
    for s in cigar_list:
        if len(s) > 1:
            cigar += str(len(s))
        cigar += s[0]
    return cigar


def create_tables(conn):
    cur = conn.cursor()
    cur.execute('PRAGMA foreign_keys = ON')
    cur.execute('''CREATE TABLE meta (
        version VARCHAR)''')

    cur.execute('INSERT INTO meta (version) VALUES (?)',
                (version, ))

    cur.execute('''CREATE TABLE gene_family (
        gene_family_id INTEGER PRIMARY KEY,
        gene_tree VARCHAR NOT NULL)''')

    cur.execute('''CREATE TABLE gene_family_member (
        gene_family_id INTEGER NOT NULL REFERENCES gene_family(gene_family_id),
        protein_id VARCHAR KEY NOT NULL REFERENCES transcript(protein_id),
        protein_alignment VARCHAR NOT NULL,
        PRIMARY KEY (gene_family_id, protein_id))''')
    conn.commit()


def align_to_db(conn, i, fname):
    cur = conn.cursor()
    for fasta_seq_align in FASTAReader_gen(fname):
        seq_id = fasta_seq_align.header[1:]
        # Trim seq_id by removing everything from the first underscore
        seq_id = seq_id.split('_', 1)[0]

        cur.execute('SELECT transcript_id, protein_id FROM transcript WHERE transcript_id=? OR protein_id=?',
                    (seq_id, seq_id))
        results = cur.fetchall()
        if len(results) == 0:
            raise Exception("Sequence id '%s' could not be found among the transcript and protein ids" % seq_id)
        elif len(results) > 1:
            raise Exception("Searching sequence id '%s' among the transcript and protein ids returned multiple results" % seq_id)
        transcript_id, protein_id = results[0]
        if protein_id is None:
            print("Skipping transcript '%s' with no protein id" % transcript_id)
        else:
            cigar = fasta_aln2cigar(fasta_seq_align.sequence)
            cur.execute('INSERT INTO gene_family_member (gene_family_id, protein_id, protein_alignment) VALUES (?, ?, ?)',
                        (i, protein_id, cigar))
            protein_sequence = fasta_seq_align.sequence.replace('-', '')
            cur.execute('UPDATE transcript SET protein_sequence=? WHERE protein_id=?', (protein_sequence, protein_id))
    conn.commit()


def newicktree_to_db(conn, i, fname):
    with open(fname) as f:
        tree = f.read().replace('\n', '')

    cur = conn.cursor()
    cur.execute('INSERT INTO gene_family (gene_family_id, gene_tree) VALUES (?, ?)',
                (i, tree))
    conn.commit()


def __main__():
    parser = optparse.OptionParser()
    parser.add_option('-t', '--tree', action='append', help='Gene tree files')
    parser.add_option('-a', '--align', action='append', help='Protein alignments in fasta_aln format')
    parser.add_option('-g', '--gene', help='Gene features file in SQLite format')
    parser.add_option('-o', '--output', help='Path of the output file')
    options, args = parser.parse_args()
    if args:
        raise Exception('Use options to provide inputs')

    if options.gene != options.output:
        shutil.copyfile(options.gene, options.output)

    conn = sqlite3.connect(options.output)
    create_tables(conn)

    for i, (tree, align) in enumerate(zip(options.tree, options.align), start=1):
        newicktree_to_db(conn, i, tree)
        align_to_db(conn, i, align)

    conn.close()


if __name__ == '__main__':
    __main__()
