import json
import optparse


def write_json(aequatus_dict, outfile=None, sort_keys=False):
    if outfile:
        with open(outfile, 'w') as f:
            json.dump(aequatus_dict, f, sort_keys=sort_keys)
    else:
        print json.dumps(aequatus_dict, indent=4, sort_keys=sort_keys)


def cigar_to_json(fname):
    cigar_dict = dict()
    with open(fname) as f:
        for element in f.readlines():
            seq_id, cigar = element.rstrip('\n').split('\t')
            cigar_dict[seq_id] = cigar
    return cigar_dict


def newicktree_to_json(fname):
    with open(fname) as f:
        return f.read().replace('\n', '')


def jsontree_to_json(fname):
    with open(fname) as f:
        return json.load(f)['tree']


def gene_to_json(fname):
    with open(fname) as f:
        return json.load(f)


def join_json(tree_dict, gene_dict, cigar_dict):
    aequatus_dict = {'tree': tree_dict,
                     'member': gene_dict}

    if cigar_dict:
        aequatus_dict['cigar'] = cigar_dict
    return aequatus_dict


def __main__():
    parser = optparse.OptionParser()
    parser.add_option('-t', '--tree', help='Tree file')
    parser.add_option('-f', '--format', type='choice', choices=['newick', 'json'], default='json', help='Tree Format')
    parser.add_option('-c', '--cigar', help='CIGAR file in table format (only if tree is in newick format)')
    parser.add_option('-g', '--gene', help='Gene file in JSON format')
    parser.add_option('-s', '--sort', action='store_true', help='Sort the keys in the JSON output')
    parser.add_option('-o', '--output', help='Path of the output file. If not specified, will print on the standard output')
    options, args = parser.parse_args()
    if args:
        raise Exception('Use options to provide inputs')

    if options.format == "newick":
        cigar_dict = cigar_to_json(options.cigar)
        tree_dict = newicktree_to_json(options.tree)
    else:
        cigar_dict = dict()
        tree_dict = jsontree_to_json(options.tree)

    gene_dict = gene_to_json(options.gene)

    aequatus_dict = join_json(tree_dict, gene_dict, cigar_dict)

    write_json(aequatus_dict, options.output, options.sort)

if __name__ == '__main__':
    __main__()
