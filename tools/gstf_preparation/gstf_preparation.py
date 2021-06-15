import json
import optparse
import os
import sqlite3
import sys

version = "0.5.0"
gene_count = 0


def asbool(val):
    if isinstance(val, str):
        val_lower = val.strip().lower()
        if val_lower in ('true', '1'):
            return True
        elif val_lower in ('false', '0'):
            return False
        else:
            raise ValueError(f"Cannot convert {val} to bool")
    else:
        return bool(val)


class Sequence:
    def __init__(self, header, sequence_parts):
        self.header = header
        self.sequence_parts = sequence_parts
        self._sequence = None

    @property
    def sequence(self):
        if self._sequence is None:
            self._sequence = ''.join(self.sequence_parts)
        return self._sequence

    def print(self, fh=sys.stdout):
        print(self.header, file=fh)
        for line in self.sequence_parts:
            print(line, file=fh)


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
            yield Sequence(header, sequence_parts)


def create_tables(conn):
    cur = conn.cursor()

    cur.execute('''CREATE TABLE meta (
        version VARCHAR PRIMARY KEY NOT NULL)''')

    cur.execute('INSERT INTO meta (version) VALUES (?)',
                (version, ))

    cur.execute('''CREATE TABLE gene (
        gene_id VARCHAR PRIMARY KEY NOT NULL,
        gene_symbol VARCHAR,
        seq_region_name VARCHAR NOT NULL,
        seq_region_start INTEGER NOT NULL,
        seq_region_end INTEGER NOT NULL,
        seq_region_strand INTEGER NOT NULL,
        species VARCHAR NOT NULL,
        biotype VARCHAR,
        gene_json VARCHAR NOT NULL)''')
    cur.execute('CREATE INDEX gene_symbol_index ON gene (gene_symbol)')

    cur.execute('''CREATE TABLE transcript (
        transcript_id VARCHAR PRIMARY KEY NOT NULL,
        transcript_symbol VARCHAR,
        protein_id VARCHAR UNIQUE,
        protein_sequence VARCHAR,
        biotype VARCHAR,
        is_canonical BOOLEAN NOT NULL DEFAULT FALSE,
        gene_id VARCHAR NOT NULL REFERENCES gene(gene_id))''')

    # The following temporary view is not used in GAFA, so schema changes to it
    # don't require a meta version upgrade.
    cur.execute('''CREATE TEMPORARY VIEW transcript_join_gene AS
        SELECT transcript_id, transcript_symbol, COALESCE(transcript.biotype, gene.biotype) AS biotype, is_canonical, gene_id, gene_symbol, seq_region_name, species
        FROM transcript JOIN gene
        USING (gene_id)''')

    cur.execute('''CREATE TABLE syntenic_region (
        species VARCHAR NOT NULL,
        syntenic_region_name VARCHAR NOT NULL,
        gene_id VARCHAR NOT NULL REFERENCES gene(gene_id),
        order_number INTEGER NOT NULL)''')

    conn.commit()


def fetch_transcript_and_gene(conn, transcript_id):
    cur = conn.cursor()

    cur.execute('SELECT * FROM transcript_join_gene WHERE transcript_id=?',
                (transcript_id, ))
    return cur.fetchone()


def remove_type_from_list_of_ids(ids):
    return ','.join(remove_type_from_id(id_) for id_ in ids.split(','))


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
            elif tag == 'representative':
                tag = 'is_canonical'
            d[tag] = value
    if cols[6] == '+':
        d['strand'] = 1
    elif cols[6] == '-':
        d['strand'] = -1
    else:
        raise Exception(f"Unrecognized strand: {cols[6]}")
    if parent_dict is not None and 'Parent' in d:
        # a 3' UTR can be split among multiple exons
        # a 5' UTR can be split among multiple exons
        # a CDS can be part of multiple transcripts
        for parent in d['Parent'].split(','):
            parent_dict.setdefault(parent, []).append(d)
    return d


def add_gene_to_dict(cols, species, gene_dict):
    global gene_count
    gene = feature_to_dict(cols)
    if not gene['id']:
        raise Exception(f"Id not found among column 9 attribute tags: {cols[8]}")
    gene.update({
        'member_id': gene_count,
        'object_type': 'Gene',
        'seq_region_name': cols[0],
        'species': species,
        'Transcript': [],
        'display_name': gene.get('Name'),
    })
    gene_dict[gene['id']] = gene
    gene_count = gene_count + 1


def add_transcript_to_dict(cols, species, transcript_dict):
    transcript = feature_to_dict(cols)
    transcript.update({
        'object_type': 'Transcript',
        'seq_region_name': cols[0],
        'species': species,
        'display_name': transcript.get('Name'),
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
            unique_cds_ids = {cds['id'] for cds in cds_list}
            if len(unique_cds_ids) > 1:
                msg = f"""Found multiple CDS IDs ({unique_cds_ids}) for transcript '{transcript_id}'.
This is not supported by the Ensembl JSON format. If a CDS is split across
multiple discontinuous genomic locations, the GFF3 standard requires that all
corresponding lines use the same ID attribute."""
                raise Exception(msg)
            cds_id = unique_cds_ids.pop()
            translation['id'] = cds_id
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
                    raise Exception(f"Transcript {transcript_id} has the start of CDS {cds_id} overlapping with the UTR end")
            else:
                translation['start'] = derived_translation_start
        if derived_translation_end is not None:
            if found_cds:
                if derived_translation_end < translation['end']:
                    raise Exception(f"Transcript {transcript_id} has the end of CDS {cds_id} overlapping with the UTR start")
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
        if 'confidence' in gene and gene['confidence'].lower() != 'high':
            print("Gene {} has confidence {} (not high), discarding".format(gene['id'], gene['confidence']), file=sys.stderr)
            continue
        gene_id = gene['id']
        cur.execute('INSERT INTO gene (gene_id, gene_symbol, seq_region_name, seq_region_start, seq_region_end, seq_region_strand, species, biotype, gene_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (gene_id, gene.get('display_name'), gene['seq_region_name'], gene['start'], gene['end'], gene['strand'], gene['species'], gene.get('biotype'), json.dumps(gene)))

        if "Transcript" in gene:
            for transcript in gene["Transcript"]:
                transcript_id = transcript['id']
                transcript_symbol = transcript.get('display_name')
                protein_id = transcript.get('Translation', {}).get('id')
                biotype = transcript.get('biotype')
                is_canonical = asbool(transcript.get('is_canonical', False))
                to_insert = (transcript_id, transcript_symbol, protein_id, biotype, is_canonical, gene_id)
                try:
                    cur.execute('INSERT INTO transcript (transcript_id, transcript_symbol, protein_id, biotype, is_canonical, gene_id) VALUES (?, ?, ?, ?, ?, ?)',
                                to_insert)
                except Exception as e:
                    raise Exception(f"Error while inserting {to_insert} into transcript table: {e}")

    conn.commit()


def remove_id_version(s, force=False):
    """
    Remove the optional '.VERSION' from an id if it's an Ensembl id or if
    `force` is True.
    """
    if force or s.startswith('ENS'):
        return s.split('.')[0]
    else:
        return s


def fetch_genomes(conn):
    """
    Fetch all the genomes from the database.
    """
    cur = conn.cursor()

    cur.execute('SELECT DISTINCT species FROM gene')

    return cur.fetchall()


def fetch_seq_region_names(conn, genome):
    """
    Fetches all the sequence region names for a genome.
    """

    cur = conn.cursor()

    cur.execute('SELECT DISTINCT seq_region_name FROM gene WHERE species=?',
                (genome, ))

    return cur.fetchall()


def populate_synteny(conn):
    """
    Populates the syntenic_region table.
    """

    cur = conn.cursor()
    cur2 = conn.cursor()

    for genome in fetch_genomes(conn):
        species = genome['species']
        for row in fetch_seq_region_names(conn, species):
            seq_region_name = row['seq_region_name']
            cur.execute(
                'SELECT gene_id FROM gene WHERE species=? AND seq_region_name=? ORDER BY seq_region_start ASC',
                (species, seq_region_name)
            )
            for order_number, gene in enumerate(cur, start=1):
                cur2.execute(
                    'INSERT INTO syntenic_region (syntenic_region_name, gene_id, species, order_number) VALUES (?, ?, ?, ?)',
                    (seq_region_name, gene["gene_id"], species, order_number)
                )
    conn.commit()


def __main__():
    parser = optparse.OptionParser()
    parser.add_option('--gff3', action='append', default=[], help='GFF3 file to convert, in SPECIES:FILENAME format. Use multiple times to add more files')
    parser.add_option('--json', action='append', default=[], help='JSON file to merge. Use multiple times to add more files')
    parser.add_option('--fasta', action='append', default=[], help='Path of the input FASTA files')
    parser.add_option('--filter', type='choice', choices=['canonical', 'coding', ''], default='', help='Which transcripts to keep')
    parser.add_option('--headers', type='choice',
                      choices=['TranscriptId_species', 'TranscriptID-GeneSymbol_species', 'TranscriptID-TranscriptSymbol_species', ''],
                      default='', help='Change the header line of the FASTA sequences to this format')
    parser.add_option('--regions', default="", help='Comma-separated list of region IDs for which FASTA sequences should be filtered')
    parser.add_option('-o', '--output', help='Path of the output SQLite file')
    parser.add_option('--of', help='Path of the output FASTA file')
    parser.add_option('--ff', default=os.devnull, help='Path of the filtered sequences output FASTA file')

    options, args = parser.parse_args()
    if args:
        raise Exception('Use options to provide inputs')

    conn = sqlite3.connect(options.output)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    create_tables(conn)

    for gff3_arg in options.gff3:
        try:
            (species, filename) = gff3_arg.split(':')
        except ValueError:
            raise Exception(f"Argument for --gff3 '{gff3_arg}' is not in the SPECIES:FILENAME format")
        gene_dict = dict()
        transcript_dict = dict()
        exon_parent_dict = dict()
        cds_parent_dict = dict()
        five_prime_utr_parent_dict = dict()
        three_prime_utr_parent_dict = dict()
        unimplemented_feature_nlines_dict = dict()

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
                    raise Exception(f"Line {i} in file '{filename}': '{line}' does not have 9 columns")
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
                    elif feature_type in unimplemented_feature_nlines_dict:
                        unimplemented_feature_nlines_dict[feature_type] += 1
                    else:
                        unimplemented_feature_nlines_dict[feature_type] = 0
                except Exception as e:
                    print(f"Line {i} in file '{filename}': {e}", file=sys.stderr)

        for unimplemented_feature, nlines in unimplemented_feature_nlines_dict.items():
            print(f"Skipped {nlines} lines in GFF3 file '{filename}': '{unimplemented_feature}' is not an implemented feature type", file=sys.stderr)

        join_dicts(gene_dict, transcript_dict, exon_parent_dict, cds_parent_dict, five_prime_utr_parent_dict, three_prime_utr_parent_dict)
        write_gene_dict_to_db(conn, gene_dict)

    for json_arg in options.json:
        with open(json_arg) as f:
            write_gene_dict_to_db(conn, json.load(f))

    # Read the FASTA files a first time to:
    # - determine for each file if we need to force the removal of the version
    #   from the transcript id
    # - fill gene_transcripts_dict when keeping only the canonical transcripts
    force_remove_id_version_file_list = []
    gene_transcripts_dict = dict()
    for fasta_arg in options.fasta:
        force_remove_id_version = False
        found_gene_transcript = False
        for entry in FASTAReader_gen(fasta_arg):
            # Extract the transcript id by removing everything after the first space and then removing the version if needed
            transcript_id = remove_id_version(entry.header[1:].lstrip().split(' ')[0], force_remove_id_version)

            transcript = fetch_transcript_and_gene(conn, transcript_id)
            if not transcript and not found_gene_transcript:
                # We have not found a proper gene transcript in this file yet,
                # try to force the removal of the version from the transcript id
                transcript_id = remove_id_version(entry.header[1:].lstrip().split(' ')[0], True)
                transcript = fetch_transcript_and_gene(conn, transcript_id)
                # Remember that we need to force the removal for this file
                if transcript:
                    force_remove_id_version = True
                    force_remove_id_version_file_list.append(fasta_arg)
                    print(f"Forcing removal of id version in FASTA file '{fasta_arg}'", file=sys.stderr)
            if not transcript:
                print(f"Transcript '{transcript_id}' in FASTA file '{fasta_arg}' not found in the gene feature information", file=sys.stderr)
                continue
            if options.filter != 'canonical':
                break
            found_gene_transcript = True

            if len(entry.sequence) % 3 != 0:
                continue
            transcript_biotype = transcript['biotype']  # This is the biotype of the transcript or, if that is NULL, the one of the gene
            if transcript_biotype and transcript_biotype != 'protein_coding':
                continue
            gene_transcripts_dict.setdefault(transcript['gene_id'], []).append((transcript_id, transcript['is_canonical'], len(entry.sequence)))

    if options.filter == 'canonical':
        selected_transcript_ids = []
        for gene_id, transcript_tuples in gene_transcripts_dict.items():
            canonical_transcript_ids = [id_ for (id_, is_canonical, _) in transcript_tuples if is_canonical]
            if not canonical_transcript_ids:
                # Select the transcript with the longest sequence. If more than
                # one transcripts have the same longest sequence for a gene, the
                # first one to appear in the FASTA file is selected.
                selected_transcript_id = max(transcript_tuples, key=lambda transcript_tuple: transcript_tuple[2])[0]
            elif len(canonical_transcript_ids) > 1:
                raise Exception(f"Gene {gene_id} has more than 1 canonical transcripts")
            else:
                selected_transcript_id = canonical_transcript_ids[0]
            selected_transcript_ids.append(selected_transcript_id)

    regions = [_.strip().lower() for _ in options.regions.split(",")]
    with open(options.of, 'w') as output_fasta_file, open(options.ff, 'w') as filtered_fasta_file:
        for fasta_arg in options.fasta:
            force_remove_id_version = fasta_arg in force_remove_id_version_file_list
            for entry in FASTAReader_gen(fasta_arg):
                transcript_id = remove_id_version(entry.header[1:].lstrip().split(' ')[0], force_remove_id_version)

                transcript = fetch_transcript_and_gene(conn, transcript_id)
                if not transcript:
                    print(f"Transcript '{transcript_id}' in FASTA file '{fasta_arg}' not found in the gene feature information", file=sys.stderr)
                    continue

                if options.filter == 'canonical':
                    # We already filtered out non-protein-coding transcripts when populating gene_transcripts_dict
                    if transcript_id not in selected_transcript_ids:
                        continue
                elif options.filter == 'coding':
                    if len(entry.sequence) % 3 != 0:
                        print(f"Transcript '{transcript_id}' in FASTA file '{fasta_arg}' has a coding sequence length which is not multiple of 3, removing from FASTA output", file=sys.stderr)
                        continue
                    transcript_biotype = transcript['biotype']  # This is the biotype of the transcript or, if that is NULL, the one of the gene
                    if transcript_biotype and transcript_biotype != 'protein_coding':
                        print(f"Transcript {transcript_id} has biotype {transcript_biotype} (not protein-coding), removing from FASTA output", file=sys.stderr)
                        continue

                if options.headers == "TranscriptId_species":
                    # Change the FASTA header to '>TranscriptId_species', as required by TreeBest
                    # Remove any underscore in the species
                    entry.header = ">{}_{}".format(transcript_id, transcript['species'].replace('_', ''))
                elif options.headers == "TranscriptID-GeneSymbol_species":
                    # Remove any underscore in the species
                    entry.header = ">{}-{}_{}".format(transcript_id, transcript['gene_symbol'], transcript['species'].replace('_', ''))
                elif options.headers == "TranscriptID-TranscriptSymbol_species":
                    # Remove any underscore in the species
                    entry.header = ">{}-{}_{}".format(transcript_id, transcript['transcript_symbol'], transcript['species'].replace('_', ''))

                if transcript['seq_region_name'].lower() in regions:
                    entry.print(filtered_fasta_file)
                else:
                    entry.print(output_fasta_file)

    populate_synteny(conn)

    conn.close()


if __name__ == '__main__':
    __main__()
