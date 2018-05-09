from __future__ import print_function

import optparse

from ete3 import PhyloTree


def main():
    usage = "usage: %prog --genetree <genetree-file> --speciestree <speciestree-file> [options]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('--genetree', help='GeneTree in nhx format')
    parser.add_option('--out_format', type='string', default='tabular', help='Choose output format')
    parser.add_option('--filters', default='', help='Filter families')

    options, args = parser.parse_args()

    if options.genetree is None:
        parser.error("--genetree option must be specified, GeneTree in nhx format")

    # reads single gene tree
    genetree = PhyloTree(options.genetree)

    leaves_list = genetree.get_leaf_names()
    # Genetree nodes are required to be in gene_species format
    leaves_list = [_ for _ in leaves_list if '_' in _]

    species_list = [_.split("_")[1] for _ in leaves_list]

    species_dict = {}
    for species in species_list:
        count = "one"
        if species in species_dict:
            count = "many"
        species_dict[species] = count

    homologies = {
        'one-to-one': [],
        'one-to-many': [],
        'many-to-one': [],
        'many-to-many': [],
        'paralogs': []
    }

    # stores relevant homology types in dict
    for i, leaf1 in enumerate(leaves_list):
        for leaf2 in leaves_list[i + 1:]:
            id1 = leaf1.split(":")[1] if ":" in leaf1 else leaf1
            id2 = leaf2.split(":")[1] if ":" in leaf2 else leaf2
            species1 = id1.split("_")[1]
            species2 = id2.split("_")[1]
            if species1 == species2:
                homology_type = 'paralogs'
            else:
                homology_type = species_dict[species1] + "-to-" + species_dict[species2]
            homologies[homology_type].append((id1, id2))

    options.filters = options.filters.split(",")

    if options.out_format == 'tabular':
        for homology_type, homologs_list in homologies.items():
            # checks if homology type is in filter
            if homology_type in options.filters:
                for (gene1, gene2) in homologs_list:
                    print("%s\t%s\t%s" % (gene1, gene2, homology_type))
    elif options.out_format == 'csv':
        print_family = True
        for homology_type, homologs_list in homologies.items():
            if homologs_list and homology_type not in options.filters:
                print_family = False

        # prints family if homology type is not found in filter
        if print_family:
            print(','.join(leaves_list))


if __name__ == "__main__":
    main()
