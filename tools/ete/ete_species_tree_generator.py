import optparse
import sys

from ete3 import NCBITaxa


parser = optparse.OptionParser()
parser.add_option('-s', '--species', dest="input_species_filename",
                  help='Species list in text format one species in each line')
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
with open(options.input_species_filename) as f:
    species_name = [_.strip().replace('_', ' ') for _ in f.readlines()]

name2taxid = ncbi.get_name_translator(species_name)

taxid = [name2taxid[_][0] for _ in species_name]

tree = ncbi.get_topology(taxid)

if options.treebest == "yes":
    inv_map = {str(v[0]): k.replace(" ", "") + "*" for k, v in name2taxid.items()}
else:
    inv_map = {str(v[0]): k for k, v in name2taxid.items()}


for leaf in tree:
    leaf.name = inv_map[leaf.name]

newickTree = tree.write(format=int(options.format))

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
