from __future__ import print_function

import json
import optparse
import sys

cds_parent_dict = dict()
exon_parent_dict = dict()
five_prime_utr_parent_dict = dict()
gene_count = 0
gene_dict = dict()
transcript_dict = dict()
three_prime_utr_parent_dict = dict()


def gene_to_json(cols, species):
    global gene_count
    gene = {
        'end': int(cols[4]),
        'member_id': gene_count,
        'object_type': 'Gene',
        'start': int(cols[3]),
        'seq_region_name': cols[0],
        'species': species,
        'strand': 1 if cols[6] == '+' else -1,
        'Transcript': [],
    }

    for attr in cols[8].split(';'):
        if '=' in attr:
            (tag, value) = attr.split('=')
            if tag == 'ID':
                gene['id'] = value
            else:
                gene[tag] = value
    gene_dict[gene['id']] = gene
    gene_count = gene_count + 1


def transcript_to_json(cols, species):
    transcript = {
        'end': int(cols[4]),
        'object_type': 'Transcript',
        'seq_region_name': cols[0],
        'species': species,
        'start': int(cols[3]),
        'strand': 1 if cols[6] == '+' else -1,
    }
    for attr in cols[8].split(';'):
        if '=' in attr:
            (tag, value) = attr.split('=')
            if tag == 'ID':
                transcript['id'] = value
            else:
                transcript[tag] = value
    transcript_dict[transcript['id']] = transcript


def exon_to_json(cols, species):
    exon = {
        'end': int(cols[4]),
        'length': int(cols[4]) - int(cols[3]) + 1,
        'object_type': 'Exon',
        'seq_region_name': cols[0],
        'species': species,
        'start': int(cols[3]),
        'strand': 1 if cols[6] == '+' else -1,
    }
    for attr in cols[8].split(';'):
        if '=' in attr:
            (tag, value) = attr.split('=')
            if tag == 'ID':
                exon['id'] = value
            else:
                exon[tag] = value

    if 'id' not in exon and 'Name' in exon:
        exon['id'] = exon['Name']

    if 'Parent' in exon:
        for parent in exon['Parent'].split(','):
            if parent not in exon_parent_dict:
                exon_parent_dict[parent] = [exon]
            else:
                exon_parent_dict[parent].append(exon)


def five_prime_utr_to_json(cols):
    five_prime_utr = {
        'start': int(cols[3]),
        'end': int(cols[4]),
    }
    for attr in cols[8].split(';'):
        if '=' in attr:
            (tag, value) = attr.split('=')
            if tag == 'ID':
                five_prime_utr['id'] = value
            else:
                five_prime_utr[tag] = value
    if 'Parent' in five_prime_utr:
        for parent in five_prime_utr['Parent'].split(','):
            five_prime_utr_parent_dict[parent] = five_prime_utr


def three_prime_utr_to_json(cols):
    three_prime_utr = {
        'start': int(cols[3]),
        'end': int(cols[4]),
    }
    for attr in cols[8].split(';'):
        if '=' in attr:
            (tag, value) = attr.split('=')
            if tag == 'ID':
                three_prime_utr['id'] = value
            else:
                three_prime_utr[tag] = value
    if 'Parent' in three_prime_utr:
        for parent in three_prime_utr['Parent'].split(','):
            three_prime_utr_parent_dict[parent] = three_prime_utr


def cds_to_json(cols):
    cds = {
        'end': int(cols[4]),
        'start': int(cols[3]),
        'strand': 1 if cols[6] == '+' else -1,
    }
    for attr in cols[8].split(';'):
        if '=' in attr:
            (tag, value) = attr.split('=')
            if tag == 'ID':
                cds['id'] = value
            else:
                cds[tag] = value
    if 'id' not in cds:
        if 'Name' in cds:
            cds['id'] = cds['Name']
        elif 'Parent' in cds:
            cds['id'] = cds['Parent']
    if 'Parent' in cds:
        # At this point we are sure than 'id' is in cds
        for parent in cds['Parent'].split(','):
            if parent not in cds_parent_dict:
                cds_parent_dict[parent] = [cds]
            else:
                cds_parent_dict[parent].append(cds)


def join_dicts():
    for parent, exon_list in exon_parent_dict.items():
        exon_list.sort(key=lambda exon: exon['start'])
        if parent in transcript_dict:
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
        found_translation = False
        if transcript_id in cds_parent_dict:
            cds_list = cds_parent_dict[transcript_id]
            cds_ids = set(_['id'] for _ in cds_list)
            if len(cds_ids) > 1:
                raise Exception("Transcript %s has multiple CDSs: this is not supported by Ensembl JSON format" % parent)
            translation['id'] = cds_ids.pop()
            cds_list.sort(key=lambda cds: cds['start'])
            translation['CDS'] = cds_list
            translation['start'] = cds_list[0]['start']
            translation['end'] = cds_list[-1]['end']
            found_translation = True
        else:
            if transcript_id in five_prime_utr_parent_dict:
                if transcript['strand'] == 1:
                    translation['start'] = five_prime_utr_parent_dict[transcript_id]['end'] + 1
                else:
                    translation['end'] = five_prime_utr_parent_dict[transcript_id]['start'] + 1

                found_translation = True
            if transcript_id in three_prime_utr_parent_dict:
                if transcript['strand'] == 1:
                    translation['end'] = three_prime_utr_parent_dict[transcript_id]['start'] - 1
                else:
                    translation['start'] = three_prime_utr_parent_dict[transcript_id]['end'] - 1
                found_translation = True
        if found_translation:
            transcript['Translation'] = translation

    for parent, five_prime_utr in five_prime_utr_parent_dict.items():
        if parent in transcript_dict:
            if 'Translation' not in transcript_dict[parent]:
                transcript_dict[parent]['Translation'] = {'start': five_prime_utr['end'] + 1}

    for parent, three_prime_utr in three_prime_utr_parent_dict.items():
        if parent in transcript_dict:
            if 'Translation' not in transcript_dict[parent]:
                transcript_dict[parent]['Translation'] = {'end': three_prime_utr['start'] - 1}

    for parent, cds_list in cds_parent_dict.items():
        if parent in transcript_dict:
            pass

    for transcript in transcript_dict.values():
        if 'Parent' in transcript and transcript['Parent'] in gene_dict:
            gene_dict[transcript['Parent']]['Transcript'].append(transcript)


def merge_dicts(json_arg):
    with open(json_arg) as f:
        dict_from_json = json.load(f)
    gene_intersection = set(gene_dict.keys()) & set(dict_from_json.keys())
    if gene_intersection:
        raise Exception("JSON file '%s' contains information for genes '%s', which are also present in other files" % (json_arg, ', '.join(gene_intersection)))
    gene_dict.update(dict_from_json)


def write_json(outfile=None, sort_keys=False):
    if outfile:
        with open(outfile, 'w') as f:
            json.dump(gene_dict, f, sort_keys=sort_keys)
    else:
        print(json.dumps(gene_dict, indent=3, sort_keys=sort_keys))


def __main__():
    parser = optparse.OptionParser()
    parser.add_option('--gff3', action='append', default=[], help='GFF3 file to convert, in SPECIES:FILENAME format. Use multiple times to add more files')
    parser.add_option('--json', action='append', default=[], help='JSON file to merge. Use multiple times to add more files')
    parser.add_option('-s', '--sort', action='store_true', help='Sort the keys in the JSON output')
    parser.add_option('-o', '--output', help='Path of the output file. If not specified, will print on the standard output')
    options, args = parser.parse_args()

    if args:
        raise Exception('Use options to provide inputs')
    for gff3_arg in options.gff3:
        try:
            (species, filename) = gff3_arg.split(':')
        except ValueError:
            raise Exception("Argument for --gff3 '%s' is not in the SPECIES:FILENAME format" % gff3_arg)
        with open(filename) as f:
            for i, line in enumerate(f):
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
                if feature_type == 'gene':
                    gene_to_json(cols, species)
                elif feature_type in ('mRNA', 'transcript'):
                    transcript_to_json(cols, species)
                elif feature_type == 'exon':
                    exon_to_json(cols, species)
                elif feature_type == 'five_prime_UTR':
                    five_prime_utr_to_json(cols)
                elif feature_type == 'three_prime_UTR':
                    three_prime_utr_to_json(cols)
                elif feature_type == 'CDS':
                    cds_to_json(cols)
                else:
                    print("Line %i in file '%s': '%s' is not an implemented feature type" % (i, filename, feature_type), file=sys.stderr)
    join_dicts()

    for json_arg in options.json:
        merge_dicts(json_arg)

    write_json(options.output, options.sort)


if __name__ == '__main__':
    __main__()
