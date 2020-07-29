from __future__ import print_function

import optparse

from ete3 import PhyloTree


def main():
    usage = "usage: %prog --genetree <genetree-file> --speciestree <speciestree-file> [options]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('--genetree', help='GeneTree in nhx format')
    parser.add_option('--speciestree', help='Species Tree in nhx format')
    parser.add_option('--species_format', type='int', default=8, help='Species Tree input format (0-9)')
    parser.add_option('--split', help='Split method')
    parser.add_option('--gene_node', type='int', default=0, help='Gene node format 0=gene_species, 1=species_gene')
    parser.add_option('--output_format', type='int', default=9, help='GeneTree output format (0-9)')
    options, args = parser.parse_args()

    if options.genetree is None:
        parser.error("--genetree option must be specified, GeneTree in nhx format")

    with open(options.genetree, 'r') as f:
        contents = f.read()

    # Remove empty NHX features that can be produced by TreeBest but break ete3
    contents = contents.replace('[&&NHX]', '')

    # reads single gene tree
    genetree = PhyloTree(contents)

    # sets species naming function
    if options.gene_node == 0:
        genetree.set_species_naming_function(parse_sp_name)

    if options.split == "dups":
        # splits tree by duplication events which returns the list of all subtrees resulting from splitting current tree by its duplication nodes.
        for cluster_id, node in enumerate(genetree.split_by_dups(), 1):
            outfile = str(cluster_id) + '_genetree.nhx'
            with open(outfile, 'w') as f:
                f.write(node.write(format=options.output_format))

    elif options.split == "treeKO":
        # splits tree by using speciation tree generated from genetree utilising treeKO tool.
        ntrees, ndups, sptrees = genetree.get_speciation_trees()
        for cluster_id, spt in enumerate(sptrees, 1):
            outfile = str(cluster_id) + '_genetree.nhx'
            with open(outfile, 'w') as f:
                f.write(spt.write(format=options.output_format))

def parse_sp_name(node_name):
    return node_name.split("_")[1]


if __name__ == "__main__":
    main()
