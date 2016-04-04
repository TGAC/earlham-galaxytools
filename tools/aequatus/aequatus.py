import json
import optparse

version = "0.0.1"


def write_json(aequatus_dict, outfile=None, sort_keys=False):
    if outfile:
        with open(outfile, 'w') as f:
            json.dump(aequatus_dict, f, sort_keys=sort_keys)
    else:
        print json.dumps(aequatus_dict, indent=4, sort_keys=sort_keys)


def cigar_to_dict(fname, gene_dict):
    cigar_dict = dict()
    with open(fname) as f:
        for element in f.readlines():
            seq_id, cigar = element.rstrip('\n').split('\t')
            cigar_dict[get_protein_id_from_transcript_id(gene_dict, seq_id)] = cigar

    return cigar_dict


def newicktree_to_string(fname):
    with open(fname) as f:
        return f.read().replace('\n', '')


def jsontree_to_dict(fname):
    with open(fname) as f:
        return json.load(f)['tree']


def gene_json_to_dict(fname):
    with open(fname) as f:
        return json.load(f)


def join_json(tree, gene_dict, cigar_dict, ref_gene, ref_protein, ref_transcript):
    aequatus_dict = {'tree': tree,
                     'member': gene_dict}

    if cigar_dict:
        aequatus_dict['cigar'] = cigar_dict

    aequatus_dict['ref'] = ref_gene
    aequatus_dict['protein_id'] = ref_protein
    aequatus_dict['transcript_id'] = ref_transcript
    aequatus_dict['version'] = version

    return aequatus_dict


def get_gene_and_transcript_ids_from_protein_id(gene_dict, protein_id):
    for gene in gene_dict.values():
        if "Transcript" in gene:
            for transcript in gene["Transcript"]:
                if 'Translation' in transcript and 'id' in transcript["Translation"]:
                    if transcript["Translation"]["id"] == protein_id:
                        return (gene["id"], transcript["id"])


def get_protein_id_from_transcript_id(gene_dict, transcript_id):
    for gene in gene_dict.values():
        if "Transcript" in gene:
            for transcript in gene["Transcript"]:
                if transcript['id'] == transcript_id:
                    if 'Translation' in transcript and 'id' in transcript['Translation']:
                        return transcript["Translation"]["id"]
                    else:
                        break


def get_first_protein_id_from_tree(tree_el):
    if "children" not in tree_el:
        return tree_el["sequence"]["id"][0]["accession"]
    else:
        # Depth-first search
        first_child = tree_el["children"][0]
        return get_first_protein_id_from_tree(first_child)


def __main__():
    parser = optparse.OptionParser()
    parser.add_option('-t', '--tree', help='Gene tree file')
    parser.add_option('-f', '--format', type='choice', choices=['newick', 'json'], default='json', help='Gene tree format')
    parser.add_option('-c', '--cigar', help='CIGAR alignments of CDS file in tabular format (only if tree is in newick format)')
    parser.add_option('-g', '--gene', help='Gene features file in JSON format')
    parser.add_option('-s', '--sort', action='store_true', help='Sort the keys in the JSON output')
    parser.add_option('-o', '--output', help='Path of the output file. If not specified, will print on the standard output')
    options, args = parser.parse_args()
    if args:
        raise Exception('Use options to provide inputs')

    gene_dict = gene_json_to_dict(options.gene)

    if options.format == "newick":
        cigar_dict = cigar_to_dict(options.cigar, gene_dict)
        tree = newicktree_to_string(options.tree)
        # Pick a random protein as reference
        ref_protein = next(iter(cigar_dict))
    else:
        cigar_dict = dict()
        tree = jsontree_to_dict(options.tree)
        ref_protein = get_first_protein_id_from_tree(tree)

    ref_gene, ref_transcript = get_gene_and_transcript_ids_from_protein_id(gene_dict, ref_protein)
    aequatus_dict = join_json(tree, gene_dict, cigar_dict, ref_gene, ref_protein, ref_transcript)

    write_json(aequatus_dict, options.output, options.sort)

if __name__ == '__main__':
    __main__()
