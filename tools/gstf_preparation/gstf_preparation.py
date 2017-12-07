from __future__ import print_function

import collections
import json
import optparse
import sqlite3
import sys

version = "0.3.0"
gene_count = 0

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
            sequence = "\n".join(sequence_parts)
            yield Sequence(header, sequence)


def create_tables(conn):
    cur = conn.cursor()

    cur.execute('''CREATE TABLE meta (
        version VARCHAR PRIMARY KEY NOT NULL)''')

    cur.execute('INSERT INTO meta (version) VALUES (?)',
                (version, ))

    cur.execute('''CREATE TABLE gene (
        gene_id VARCHAR PRIMARY KEY NOT NULL,
        gene_symbol VARCHAR,
        species VARCHAR NOT NULL,
        gene_json VARCHAR NOT NULL)''')
    cur.execute('CREATE INDEX gene_symbol_index ON gene (gene_symbol)')

    cur.execute('''CREATE TABLE transcript (
        transcript_id VARCHAR PRIMARY KEY NOT NULL,
        protein_id VARCHAR UNIQUE,
        protein_sequence VARCHAR,
        gene_id VARCHAR NOT NULL REFERENCES gene(gene_id))''')

    cur.execute('''CREATE VIEW transcript_species AS
        SELECT transcript_id, species
        FROM transcript JOIN gene
        ON transcript.gene_id = gene.gene_id''')

    conn.commit()


def remove_type_from_list_of_ids(l):
    return ','.join(remove_type_from_id(_) for _ in l.split(','))


def remove_type_from_id(id_):
    colon_index = id_.find(':')
    if colon_index >= 0:
        return id_[colon_index + 1:]
    else:
        return id_


def feature_to_dict(cols, parent_dict=None):
    d = {
        'end': int(cols[4]),
        'start': int(cols[3]),
    }
    for attr in cols[8].split(';'):
        if '=' in attr:
            (tag, value) = attr.split('=')
            if tag == 'ID':
                tag = 'id'
                value = remove_type_from_id(value)
            elif tag == 'Parent':
                value = remove_type_from_list_of_ids(value)
            d[tag] = value
    if cols[6] == '+':
        d['strand'] = 1
    elif cols[6] == '-':
        d['strand'] = -1
    else:
        raise Exception("Unrecognized strand '%s'" % cols[6])
    if parent_dict is not None and 'Parent' in d:
        # a 3' UTR can be split among multiple exons
        # a 5' UTR can be split among multiple exons
        # a CDS can be part of multiple transcripts
        for parent in d['Parent'].split(','):
            if parent not in parent_dict:
                parent_dict[parent] = [d]
            else:
                parent_dict[parent].append(d)
    return d


def add_gene_to_dict(cols, species, gene_dict):
    global gene_count
    gene = feature_to_dict(cols)
    gene.update({
        'member_id': gene_count,
        'object_type': 'Gene',
        'seq_region_name': cols[0],
        'species': species,
        'Transcript': [],
        'display_name': gene.get('Name', None)
    })
    if gene['id']:
        gene_dict[gene['id']] = gene
        gene_count = gene_count + 1


def add_transcript_to_dict(cols, species, transcript_dict):
    transcript = feature_to_dict(cols)
    transcript.update({
        'object_type': 'Transcript',
        'seq_region_name': cols[0],
        'species': species,
    })
    transcript_dict[transcript['id']] = transcript


def add_exon_to_dict(cols, species, exon_parent_dict):
    exon = feature_to_dict(cols, exon_parent_dict)
    exon.update({
        'length': int(cols[4]) - int(cols[3]) + 1,
        'object_type': 'Exon',
        'seq_region_name': cols[0],
        'species': species,
    })
    if 'id' not in exon and 'Name' in exon:
        exon['id'] = exon['Name']


def add_cds_to_dict(cols, cds_parent_dict):
    cds = feature_to_dict(cols, cds_parent_dict)
    if 'id' not in cds:
        if 'Name' in cds:
            cds['id'] = cds['Name']
        elif 'Parent' in cds and ',' not in cds['Parent']:
            cds['id'] = cds['Parent']


def join_dicts(gene_dict, transcript_dict, exon_parent_dict, cds_parent_dict, five_prime_utr_parent_dict, three_prime_utr_parent_dict):
    for parent, exon_list in exon_parent_dict.items():
        if parent in transcript_dict:
            exon_list.sort(key=lambda _: _['start'])
            transcript_dict[parent]['Exon'] = exon_list

    for transcript_id, transcript in transcript_dict.items():
        translation = {
            'CDS': [],
            'id': None,
            'end': transcript['end'],
            'object_type': 'Translation',
            'species': transcript['species'],
            'start': transcript['start'],
        }
        found_cds = False
        derived_translation_start = None
        derived_translation_end = None
        if transcript_id in cds_parent_dict:
            cds_list = cds_parent_dict[transcript_id]
            cds_ids = set(_['id'] for _ in cds_list)
            if len(cds_ids) > 1:
                raise Exception("Transcript %s has multiple CDSs: this is not supported by Ensembl JSON format" % parent)
            translation['id'] = cds_ids.pop()
            cds_list.sort(key=lambda _: _['start'])
            translation['CDS'] = cds_list
            translation['start'] = cds_list[0]['start']
            translation['end'] = cds_list[-1]['end']
            found_cds = True
        if transcript_id in five_prime_utr_parent_dict:
            five_prime_utr_list = five_prime_utr_parent_dict[transcript_id]
            five_prime_utr_list.sort(key=lambda _: _['start'])
            if transcript['strand'] == 1:
                derived_translation_start = five_prime_utr_list[-1]['end'] + 1
            else:
                derived_translation_end = five_prime_utr_list[0]['start'] - 1
        if transcript_id in three_prime_utr_parent_dict:
            three_prime_utr_list = three_prime_utr_parent_dict[transcript_id]
            three_prime_utr_list.sort(key=lambda _: _['start'])
            if transcript['strand'] == 1:
                derived_translation_end = three_prime_utr_list[0]['start'] - 1
            else:
                derived_translation_start = three_prime_utr_list[-1]['end'] + 1
        if derived_translation_start is not None:
            if found_cds:
                if derived_translation_start > translation['start']:
                    raise Exception("UTR overlaps with CDS")
            else:
                translation['start'] = derived_translation_start
        if derived_translation_end is not None:
            if found_cds:
                if derived_translation_end < translation['end']:
                    raise Exception("UTR overlaps with CDS")
            else:
                translation['end'] = derived_translation_end
        if found_cds or derived_translation_start is not None or derived_translation_end is not None:
            transcript['Translation'] = translation

    for transcript in transcript_dict.values():
        if 'Parent' in transcript:
            # A polycistronic transcript can have multiple parents
            for parent in transcript['Parent'].split(','):
                if parent in gene_dict:
                    gene_dict[parent]['Transcript'].append(transcript)


def write_gene_dict_to_db(conn, gene_dict):
    cur = conn.cursor()

    for gene in gene_dict.values():
        if gene is None:
            # This can happen when loading a JSON file from Ensembl
            continue
        gene_id = gene['id']
        cur.execute('INSERT INTO gene (gene_id, gene_symbol, species, gene_json) VALUES (?, ?, ?, ?)',
                    (gene_id, gene.get('display_name', None), gene['species'], json.dumps(gene)))

        if "Transcript" in gene:
            for transcript in gene["Transcript"]:
                transcript_id = transcript['id']
                protein_id = transcript.get('Translation', {}).get('id', None)
                try:
                    cur.execute('INSERT INTO transcript (transcript_id, protein_id, gene_id) VALUES (?, ?, ?)',
                                (transcript_id, protein_id, gene_id))
                except Exception as e:
                    raise Exception("Error while inserting (%s, %s, %s) into transcript table: %s" % (transcript_id, protein_id, gene_id, e))

    conn.commit()


def fetch_species_for_transcript(conn, transcript_id):
    cur = conn.cursor()

    cur.execute('SELECT species FROM transcript_species WHERE transcript_id=?',
                (transcript_id, ))
    results = cur.fetchone()
    if not results:
        return None
    return results[0]


def fetch_gene_id_for_transcript(conn, transcript_id):
    cur = conn.cursor()

    cur.execute('SELECT gene_id FROM transcript WHERE transcript_id=?',
                (transcript_id, ))
    results = cur.fetchone()
    if not results:
        return None
    return results[0]


def remove_id_version(s):
    """
    Remove the optional '.VERSION' from an Ensembl id.
    """
    if s.startswith('ENS'):
        return s.split('.')[0]
    else:
        return s


def __main__():
    parser = optparse.OptionParser()
    parser.add_option('--gff3', action='append', default=[], help='GFF3 file to convert, in SPECIES:FILENAME format. Use multiple times to add more files')
    parser.add_option('--json', action='append', default=[], help='JSON file to merge. Use multiple times to add more files')
    parser.add_option('--fasta', action='append', default=[], help='Path of the input FASTA files')
    parser.add_option('-l', action='store_true', default=False, dest='longestCDS', help='Keep only the longest CDS per gene')
    parser.add_option('--headers', action='store_true', default=False, help='Change the header line of the FASTA sequences to the >TranscriptId_species format')
    parser.add_option('-o', '--output', help='Path of the output SQLite file')
    parser.add_option('--of', help='Path of the output FASTA file')
    options, args = parser.parse_args()
    if args:
        raise Exception('Use options to provide inputs')

    conn = sqlite3.connect(options.output)
    conn.execute('PRAGMA foreign_keys = ON')
    create_tables(conn)

    for gff3_arg in options.gff3:
        try:
            (species, filename) = gff3_arg.split(':')
        except ValueError:
            raise Exception("Argument for --gff3 '%s' is not in the SPECIES:FILENAME format" % gff3_arg)
        gene_dict = dict()
        transcript_dict = dict()
        exon_parent_dict = dict()
        cds_parent_dict = dict()
        five_prime_utr_parent_dict = dict()
        three_prime_utr_parent_dict = dict()

        with open(filename) as f:
            for i, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    # skip empty lines
                    continue
                if line[0] == '#':
                    # skip comment lines
                    continue
                cols = line.split('\t')
                if len(cols) != 9:
                    raise Exception("Line %i in file '%s': '%s' does not have 9 columns" % (i, filename, line))
                feature_type = cols[2]
                try:
                    if feature_type == 'gene':
                        add_gene_to_dict(cols, species, gene_dict)
                    elif feature_type in ('mRNA', 'transcript'):
                        add_transcript_to_dict(cols, species, transcript_dict)
                    elif feature_type == 'exon':
                        add_exon_to_dict(cols, species, exon_parent_dict)
                    elif feature_type == 'five_prime_UTR':
                        feature_to_dict(cols, five_prime_utr_parent_dict)
                    elif feature_type == 'three_prime_UTR':
                        feature_to_dict(cols, three_prime_utr_parent_dict)
                    elif feature_type == 'CDS':
                        add_cds_to_dict(cols, cds_parent_dict)
                    else:
                        print("Line %i in file '%s': '%s' is not an implemented feature type" % (i, filename, feature_type), file=sys.stderr)
                except Exception as e:
                    print("Line %i in file '%s': %s" % (i, filename, e), file=sys.stderr)

        join_dicts(gene_dict, transcript_dict, exon_parent_dict, cds_parent_dict, five_prime_utr_parent_dict, three_prime_utr_parent_dict)
        write_gene_dict_to_db(conn, gene_dict)

    for json_arg in options.json:
        with open(json_arg) as f:
            write_gene_dict_to_db(conn, json.load(f))

    if options.longestCDS:
        gene_transcripts_dict = dict()
        for fasta_arg in options.fasta:
            for entry in FASTAReader_gen(fasta_arg):
                # Extract the transcript id by removing everything after the first space and then removing the version if it is an Ensembl id
                transcript_id = remove_id_version(entry.header[1:].lstrip().split(' ')[0])

                gene_id = fetch_gene_id_for_transcript(conn, transcript_id)
                if not gene_id:
                    continue

                if gene_id in gene_transcripts_dict:
                    gene_transcripts_dict[gene_id].append((transcript_id, len(entry.sequence)))
                else:
                    gene_transcripts_dict[gene_id] = [(transcript_id, len(entry.sequence))]

        # For each gene, select the transcript with the longest sequence
        # If more than one transcripts have the same longest sequence for a gene, the
        # first one to appear in the FASTA file is selected
        selected_transcript_ids = [max(transcript_id_lengths, key=lambda _: _[1])[0] for transcript_id_lengths in gene_transcripts_dict.values()]

    with open(options.of, 'w') as output_fasta_file:
        for fasta_arg in options.fasta:
            for entry in FASTAReader_gen(fasta_arg):
                transcript_id = remove_id_version(entry.header[1:].lstrip().split(' ')[0])
                if options.longestCDS and transcript_id not in selected_transcript_ids:
                    continue

                species_for_transcript = fetch_species_for_transcript(conn, transcript_id)
                if not species_for_transcript:
                    print("Transcript '%s' not found in the gene feature information" % transcript_id, file=sys.stderr)
                    continue

                if options.headers:
                    # Change the FASTA header to '>TranscriptId_species', as required by TreeBest
                    # Remove any underscore in the species
                    header = ">%s_%s" % (transcript_id, species_for_transcript.replace('_', ''))
                else:
                    header = entry.header

                output_fasta_file.write("%s\n%s\n" % (header, entry.sequence))

    conn.close()


if __name__ == '__main__':
    __main__()
