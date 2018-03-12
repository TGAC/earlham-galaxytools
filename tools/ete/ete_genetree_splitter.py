from __future__ import print_function

import optparse

from ete3 import PhyloTree


def main():
    usage = "usage: %prog --genetree <genetree-file> --speciestree <speciestree-file> [options]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('--genetree', help='GeneTree in nhx format')
    parser.add_option('--speciestree', help='Species Tree in nhx format')
    parser.add_option('--species_format', type='int', default=8, help='Species Tree input format (0-9)')
    parser.add_option('--gene_node', type='int', default=0, help='Gene node format 0=gene_species, 1=species_gene')
    parser.add_option('--gainlose', action='store_true', default=False, help='Find out gene gain/lose')
    parser.add_option('--output_format', type='int', default=9, help='GeneTree output format (0-9)')
    options, args = parser.parse_args()

    if options.genetree is None:
        parser.error("--genetree option must be specified, GeneTree in nhx format")

    # reads single gene tree
    genetree = PhyloTree(options.genetree)

    # sets species naming function
    if options.gene_node == 0:
        genetree.set_species_naming_function(parse_sp_name)

    # reconcile species tree with gene tree to help find out gene gain/lose
    if options.gainlose:

        if options.speciestree is None:
            parser.error("--speciestree option must be specified, species tree in nhx format")

        # reads species tree
        speciestree = PhyloTree(options.speciestree, format=options.species_format)

        # Removes '*' from Species names comes from Species tree configrured for TreeBest
        for leaf in speciestree:
            leaf.name = leaf.name.strip('*')

        genetree, events = genetree.reconcile(speciestree)

    # splits tree by duplication events which returns the list of all subtrees resulting from splitting current tree by its duplication nodes.
    for cluster_id, node in enumerate(genetree.split_by_dups(), 1):
        outfile = str(cluster_id) + '_genetree.nhx'
        with open(outfile, 'w') as f:
            f.write(node.write(format=options.output_format))


def parse_sp_name(node_name):
    return node_name.split("_")[1]


if __name__ == "__main__":
    main()
