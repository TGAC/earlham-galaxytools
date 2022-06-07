from __future__ import print_function

import optparse
import os
import sys

from ete3 import PhyloTree


def main():
    usage = "usage: %prog --genetree <genetree-file> --speciestree <speciestree-file> [options]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('--genetree', help='GeneTree in nhx format')
    parser.add_option('--speciestree', help='Species Tree in nhx format')
    parser.add_option('--ingroup', help='Species Tree in nhx format')
    parser.add_option('--outgroup', help='Species Tree in nhx format')
    parser.add_option('--species_format', type='int', default=8, help='Species Tree input format (0-9)')
    parser.add_option('--gene_node', type='int', default=0, help='Gene node format 0=gene_species, 1=species_gene')
    parser.add_option('--gainlose', action='store_true', default=False, help='Find out gene gain/lose')
    parser.add_option('--split', type='choice', choices=['dups', 'treeko', 'species'], dest="split", default='dups', help='Choose GeneTree splitting algorithms')
    parser.add_option('--output_format', type='int', default=9, help='GeneTree output format (0-9)')
    parser.add_option('-d', '--dir', type='string', default="", help="Absolute or relative path to output directory. If directory does not exist it will be created")

    options, args = parser.parse_args()

    if options.dir and not os.path.exists(options.dir):
        os.makedirs(options.dir)

    if options.genetree is None:
        parser.error("--genetree option must be specified, GeneTree in nhx format")

    if os.stat(options.genetree).st_size == 0:
        sys.exit()

    with open(options.genetree, 'r') as f:
        contents = f.read()

    # Remove empty NHX features that can be produced by TreeBest but break ete3
    contents = contents.replace('[&&NHX]', '')

    # reads single gene tree
    genetree = PhyloTree(contents)

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

    if options.split == "dups":
        # splits tree by duplication events which returns the list of all subtrees resulting from splitting current tree by its duplication nodes.
        for cluster_id, node in enumerate(genetree.split_by_dups(), start=1):
            outfile = '{}_genetree.nhx'.format(cluster_id)
            if options.dir:
                outfile = os.path.join(options.dir, outfile)
            with open(outfile, 'w') as f:
                f.write(node.write(format=options.output_format))
    elif options.split == "treeko":
        # splits tree using the TreeKO algorithm.
        ntrees, ndups, sptrees = genetree.get_speciation_trees()

        for cluster_id, spt in enumerate(sptrees, start=1):
            outfile = '{}_genetree.nhx'.format(cluster_id)
            if options.dir:
                outfile = os.path.join(options.dir, outfile)
            with open(outfile, 'w') as f:
                f.write(spt.write(format=options.output_format))
    elif options.split == "species":
        ingroup = options.ingroup.split(",")
        outgroup = options.outgroup.split(",")
        cluster_id = 0

        def split_tree_by_species(tree, ingroup, outgroup):
            nonlocal cluster_id

            if len(outgroup) > 0:
                outgroup_bool = check_outgroup(tree, outgroup)
            else:
                outgroup_bool = True

            if outgroup_bool and check_ingroup(tree, ingroup):
                child1, child2 = tree.children
                split_tree_by_species(child1, ingroup, outgroup)
                split_tree_by_species(child2, ingroup, outgroup)
            else:
                cluster_id += 1
                outfile = '{}_genetree.nhx'.format(cluster_id)
                if options.dir:
                    outfile = os.path.join(options.dir, outfile)
                with open(outfile, 'w') as f:
                    f.write(tree.write(format=options.output_format))

        split_tree_by_species(genetree, ingroup, outgroup)


def check_outgroup(tree, outgroup):
    species = get_species(tree)

    count = 0

    for out in outgroup:
        if species.count(out) > 1:
            count = count + 1

    return count >= len(outgroup) / 2


def check_ingroup(tree, ingroup):
    species = get_species(tree)

    count = 0

    for ing in ingroup:
        if species.count(ing) > 1:
            count = count + 1

    return count > 0 and len(ingroup) / count >= 0.8


def parse_sp_name(node_name):
    return node_name.split("_")[-1]


def get_species(node):
    leaves_list = node.get_leaf_names()
    # Genetree nodes are required to be in gene_species format
    leaves_list = [_ for _ in leaves_list if '_' in _]

    species_list = [_.split("_")[-1] for _ in leaves_list]

    return species_list


if __name__ == "__main__":
    main()
