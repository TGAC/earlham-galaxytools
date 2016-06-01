from ete3 import Tree
from ete3 import NCBITaxa
import optparse


ncbi = NCBITaxa()

species_name = []
taxid = []

parser = optparse.OptionParser()
parser.add_option('-s', '--species', dest="input_species_filename",
                  help='Species list in text format one species in each line')

parser.add_option('-f', '--format', type='choice', choices=['0','1','2','3','4','5','6','7','8','9','100'], dest="format",
                  default='8', help='outpur format for tree')

parser.add_option('-t', '--treebest', type='choice', choices=['yes','no'], dest="treebest",
                  default='no', help='To be used in TreeBest')

options, args = parser.parse_args()

if options.input_species_filename is None:
    raise Exception('-s option must be specified, Species list in text format one species in each line')


with open(options.input_species_filename) as f:
    species_name = f.readlines()


for index, species in enumerate(species_name):
    species_name[index] = species.strip().replace("_", " ")


name2taxid = ncbi.get_name_translator(species_name)

for species in species_name:
	taxid.append(name2taxid[species][0])

tree = ncbi.get_topology(taxid)

if(options.treebest == "yes"):
	inv_map = {str(v[0]): k.replace(" ", "")+"*" for k, v in name2taxid.items()}
else:
	inv_map = {str(v[0]): k for k, v in name2taxid.items()}


for leaf in tree:
    leaf.add_features(name=inv_map.get(leaf.name, "none"))

newickTree = tree.write(format=int(options.format)).replace(";","")

if(options.treebest == "yes"):
  newickTree = newickTree+"root;"

print newickTree


