from __future__ import print_function

import json
import optparse
import sys

gene_count = 0


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
    })
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


def update_full_gene_dict_no_overwrite(full_gene_dict, gene_dict):
    gene_intersection = set(full_gene_dict.keys()) & set(gene_dict.keys())
    if gene_intersection:
        raise Exception("Information for genes '%s' are present in multiple files" % ', '.join(gene_intersection))
    full_gene_dict.update(gene_dict)


def write_json(full_gene_dict, outfile=None, sort_keys=False):
    if outfile:
        with open(outfile, 'w') as f:
            json.dump(full_gene_dict, f, sort_keys=sort_keys)
    else:
        json.dump(full_gene_dict, sys.stdout, sort_keys=sort_keys)


def __main__():
    parser = optparse.OptionParser()
    parser.add_option('--gff3', action='append', default=[], help='GFF3 file to convert, in SPECIES:FILENAME format. Use multiple times to add more files')
    parser.add_option('--json', action='append', default=[], help='JSON file to merge. Use multiple times to add more files')
    parser.add_option('-s', '--sort', action='store_true', help='Sort the keys in the JSON output')
    parser.add_option('-o', '--output', help='Path of the output file. If not specified, will print on the standard output')
    options, args = parser.parse_args()
    if args:
        raise Exception('Use options to provide inputs')

    full_gene_dict = dict()
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
                    raise Exception("Line %i in file '%s': %s" % (i, filename, e))
        join_dicts(gene_dict, transcript_dict, exon_parent_dict, cds_parent_dict, five_prime_utr_parent_dict, three_prime_utr_parent_dict)
        update_full_gene_dict_no_overwrite(full_gene_dict, gene_dict)

    for json_arg in options.json:
        with open(json_arg) as f:
            update_full_gene_dict_no_overwrite(full_gene_dict, json.load(f))

    write_json(full_gene_dict, options.output, options.sort)


if __name__ == '__main__':
    __main__()
