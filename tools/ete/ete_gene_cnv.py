from __future__ import print_function

import collections
import argparse

from ete3 import PhyloTree


def printCSV(myDict, speciesList, colList=None):
    """ Pretty print a list of dictionaries (myDict) as a dynamically sized table.
    If column names (colList) aren't specified, they will show in random order.
    Author: Thierry Husson - Use it as you want but don't blame me.
    """
    colList = ["gene"]
    colList.extend(speciesList)

    if not colList:
        colList = list(myDict[0].keys() if myDict else [])

    myList = [colList]

    for item in myDict:
        myList.append([str(item[col] if item[col] is not None else '') for col in colList])

    for item in myList:
        print(*item, sep=", ")


def main():
    usage = "usage: %prog --genetree <genetree-file> [options]"
    parser = argparse.ArgumentParser(description='Gene Copy Number Finder')
    parser.add_argument('--genetree', help='GeneTree in nhx format')
    parser.add_argument('--speciesorder', help='Comma separated species list')
    args = parser.parse_args()

    if args.genetree is None:
        parser.error("--genetree option must be specified, GeneTree in nhx format")

    if args.speciesorder is None:
        parser.error("--speciesorder option must be specified, Comma separated species list")

    f = open(args.genetree, "r")

    speciesList = args.speciesorder.split(",")

    table = []

    # reads multiple gene tree line by line gene tree
    for row in f:

        contents = row

        # Remove empty NHX features that can be produced by TreeBest but break ete3
        contents = contents.replace('[&&NHX]', '')

        # reads single gene tree
        genetree = PhyloTree(contents)

        leaves = genetree.get_leaf_names()

        # Genetree nodes are required to be in gene_species format
        leaves_list = [_ for _ in leaves if '_' in _]

        ref_species = speciesList[0]

        species_list = [_.split("_")[1] for _ in leaves]

        counter = collections.Counter(species_list)

        if counter[ref_species] == 0:
            for s in speciesList:
                if counter[s] > 0:
                    ref_species = s
                    break

        for x in leaves_list:
            if x.split("_")[1] == ref_species and counter[ref_species] > 0:
                counter['gene'] = x.split("_")[0]
                break

        table.append(counter)

    printCSV(table, speciesList)


if __name__ == "__main__":
    main()
