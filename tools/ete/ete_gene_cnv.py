from __future__ import print_function

import argparse
import collections

from ete3 import PhyloTree


def printTSV(myDict, colList=None):
    """ Pretty print a list of dictionaries (myDict) as a dynamically sized table.
    If column names (colList) aren't specified, they will show in random order.
    Author: Thierry Husson - Use it as you want but don't blame me.
    """
    if not colList:
        colList = list(myDict[0].keys() if myDict else [])

    myList = [colList]

    for item in myDict:
        myList.append([str(item[col] if item[col] is not None else '') for col in colList])

    for item in myList:
        print(*item, sep="\t")


def main():
    parser = argparse.ArgumentParser(description='Gene Copy Number Finder')
    parser.add_argument('--genetree', required=True, help='GeneTree in nhx format')
    parser.add_argument('--speciesorder', required=True, help='Comma-separated species list')
    args = parser.parse_args()

    species_list = args.speciesorder.split(",")
    species_list = [_.strip() for _ in species_list]
    table = []

    with open(args.genetree, "r") as f:
        # reads multiple gene tree line by line gene tree
        for line in f:
            # Remove empty NHX features that can be produced by TreeBest but break ete3
            line = line.replace('[&&NHX]', '')

            # reads single gene tree
            genetree = PhyloTree(line)
            leaves = genetree.get_leaf_names()

            leaves_parts = [_.split("_") for _ in leaves]
            for i, leaf_parts in enumerate(leaves_parts):
                if len(leaf_parts) != 2:
                    raise Exception("Leaf node '%s' is not in gene_species format" % leaves[i])

            leaves_species = [_[-1] for _ in leaves_parts]
            species_counter = collections.Counter(leaves_species)

            # Assign to ref_species the first element of species_list which
            # appears in a leaf node
            for ref_species in species_list:
                if ref_species in species_counter:
                    break
            else:
                raise Exception("None of the specified species was found in the GeneTree '%s'" % line)

            # Find the gene of the (first) leaf node for the ref_species
            for leaf_parts in leaves_parts:
                if leaf_parts[-1] == ref_species:
                    species_counter['gene'] = leaf_parts[:-1]
                    break

            table.append(species_counter)

    colList = ["gene"] + species_list
    printTSV(table, colList)


if __name__ == "__main__":
    main()
