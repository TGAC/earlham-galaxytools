from __future__ import print_function

import json
import optparse
import sqlite3

version = "0.2.0"


def create_tables(conn):
    cur = conn.cursor()
    cur.execute('PRAGMA foreign_keys = ON')
    cur.execute('''CREATE TABLE gene_family (
        gene_family_id INTEGER PRIMARY KEY,
        gene_tree VARCHAR NOT NULL)''')

    cur.execute('''CREATE TABLE gene (
        gene_id VARCHAR PRIMARY KEY NOT NULL,
        gene_symbol VARCHAR,
        gene_json VARCHAR NOT NULL)''')
    cur.execute('CREATE INDEX gene_symbol_index ON gene (gene_symbol)')

    cur.execute('''CREATE TABLE transcript (
        transcript_id VARCHAR PRIMARY KEY NOT NULL,
        protein_id VARCHAR UNIQUE,
        gene_id VARCHAR NOT NULL REFERENCES gene(gene_id))''')

    cur.execute('''CREATE TABLE gene_family_member (
        gene_family_id INTEGER NOT NULL REFERENCES gene_family(gene_family_id),
        protein_id VARCHAR KEY NOT NULL REFERENCES transcript(protein_id),
        alignment VARCHAR NOT NULL,
        PRIMARY KEY (gene_family_id, protein_id))''')
    conn.commit()


def cigar_to_db(conn, i, fname):
    cur = conn.cursor()
    with open(fname) as f:
        for element in f.readlines():
            seq_id, cigar = element.rstrip('\n').split('\t')
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
                cur.execute('INSERT INTO gene_family_member (gene_family_id, protein_id, alignment) VALUES (?, ?, ?)',
                            (i, protein_id, cigar))
                conn.commit()


def newicktree_to_db(conn, i, fname):
    with open(fname) as f:
        tree = f.read().replace('\n', '')

    cur = conn.cursor()
    cur.execute('INSERT INTO gene_family (gene_family_id, gene_tree) VALUES (?, ?)',
                (i, tree))
    conn.commit()


def gene_json_to_db(conn, fname):
    with open(fname) as f:
        all_genes_dict = json.load(f)

    cur = conn.cursor()
    for gene_dict in all_genes_dict.values():
        gene_id = gene_dict['id']
        gene_symbol = gene_dict.get('display_name', None)
        cur.execute("INSERT INTO gene (gene_id, gene_symbol, gene_json) VALUES (?, ?, ?)",
                    (gene_id, gene_symbol, json.dumps(gene_dict)))

        if "Transcript" in gene_dict:
            for transcript in gene_dict["Transcript"]:
                transcript_id = transcript['id']
                if 'Translation' in transcript and 'id' in transcript['Translation']:
                    protein_id = transcript["Translation"]["id"]
                else:
                    protein_id = None
                cur.execute("INSERT INTO transcript (transcript_id, protein_id, gene_id) VALUES (?, ?, ?)",
                            (transcript_id, protein_id, gene_id))
    conn.commit()


def __main__():
    parser = optparse.OptionParser()
    parser.add_option('-t', '--tree', action='append', help='Gene tree files')
    parser.add_option('-c', '--cigar', action='append', help='CIGAR alignments of CDS files in tabular format')
    parser.add_option('-g', '--gene', help='Gene features file in JSON format')
    parser.add_option('-o', '--output', help='Path of the output file')
    options, args = parser.parse_args()
    if args:
        raise Exception('Use options to provide inputs')

    conn = sqlite3.connect(options.output)
    create_tables(conn)

    gene_json_to_db(conn, options.gene)

    for i, (tree, cigar) in enumerate(zip(options.tree, options.cigar), start=1):
        newicktree_to_db(conn, i, tree)
        cigar_to_db(conn, i, cigar)


if __name__ == '__main__':
    __main__()
