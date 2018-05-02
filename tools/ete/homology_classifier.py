from __future__ import print_function

import optparse

from ete3 import PhyloTree


def main():
    usage = "usage: %prog --genetree <genetree-file> --speciestree <speciestree-file> [options]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('--genetree', help='GeneTree in nhx format')
    parser.add_option('--out_format', type='string', default='tabular', help='Choose output format')
    parser.add_option('--filters', default=[], help='Filter families')

    options, args = parser.parse_args()

    if options.genetree is None:
        parser.error("--genetree option must be specified, GeneTree in nhx format")

    # reads single gene tree
    genetree = PhyloTree(options.genetree)

    leaves_list = genetree.get_leaf_names()

    species_list = []
    gene_lose_list = []

    for i, val in enumerate(leaves_list):
        if '_' in leaves_list[i]:
            species_list.append(leaves_list[i].split("_")[1])
        else:
            gene_lose_list.append(i)

    leaves_list = [i for j, i in enumerate(leaves_list) if j not in gene_lose_list]

    species_dict = {}

    for val in species_list:
        count = "one"
        if val in species_dict:
            count = "many"
        species_dict[val] = count

    homologis = {
        'one-to-one': [],
        'one-to-many': [],
        'many-to-one': [],
        'many-to-many': [],
        'paralogs': []
    }

    # stores relevant homolgy types in dict
    for i, val in enumerate(leaves_list):
        for j in range(i+1, len(leaves_list)):
            id1 = leaves_list[i].split(":")[1] if ":" in leaves_list[i] else leaves_list[i]
            id2 = leaves_list[j].split(":")[1] if ":" in leaves_list[j] else leaves_list[j]
            if(id1.split("_")[1] == id2.split("_")[1]):
                homologis["paralogs"].append({id1: id2})
            else:
                homologis[species_dict[id1.split("_")[1]]+"-to-"+species_dict[id2.split("_")[1]]].append({id1: id2})

    options.filters = options.filters.split(",")

    if options.out_format == 'tabular':
        for homology, homologs in homologis.items():
            # checks if homology type is in filter
            if homology in options.filters:
                for element in homologis[homology]:
                    for key, value in element.items():
                        print(key+"\t"+value+"\t"+homology)

    elif options.out_format == 'csv':
        flag = False
        for homology, homologs in homologis.items():
            if len(homologs) > 0 and homology in options.filters:
                flag = True

        # prints family if homology type is not found in filter
        if not flag:
            print(','.join(leaves_list))


if __name__ == "__main__":
    main()
