import optparse
import sys

from ete3 import NCBITaxa


parser = optparse.OptionParser()
parser.add_option('-s', '--species', dest="input_species_filename",
                  help='List of species names of taxids in text format one species in each line')
parser.add_option('-d', '--database', dest="database", default=None,
                  help='ETE sqlite data base to use (default: ~/.etetoolkit/taxa.sqlite)')
parser.add_option('-o', '--output', dest="output", help='output file name (default: stdout)')
parser.add_option('-f', '--format', type='choice', choices=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '100'], dest="format",
                  default='8', help='outpur format for tree')
parser.add_option('-t', '--treebest', type='choice', choices=['yes', 'no'], dest="treebest",
                  default='no', help='To be used in TreeBest')
options, args = parser.parse_args()
if options.input_species_filename is None:
    parser.error("-s option must be specified, Species list in text format one species in each line")

ncbi = NCBITaxa(dbfile=options.database)

# determine taxids and species names in the input file
names = []
taxids = []
with open(options.input_species_filename) as f:
    for species in f:
        species = species.strip().replace('_', ' ')
        try:
            taxids.append(int(species))
        except ValueError:
            names.append(species)
# translate all species names to taxids
name2taxid = ncbi.get_name_translator(names)
taxids += {name2taxid[n][0] for n in names}

# get topology and set the scientific name as output
tree = ncbi.get_topology(taxids)
for isleaf, node in tree.iter_prepostorder():
    node.name = node.sci_name

if options.treebest == "yes":
    for leaf in tree:
        leaf.name = leaf.name.replace(" ", "") + "*"

newickTree = tree.write(format=int(options.format))
# print(type(tree))
if options.treebest == "yes":
    newickTree = newickTree.rstrip(';')
    newickTree = newickTree + "root;"
# setup output
if not options.output:   # if filename is not given
    of = sys.stdout
else:
    of = open(options.output, "w")
of.write(newickTree)
of.close()
