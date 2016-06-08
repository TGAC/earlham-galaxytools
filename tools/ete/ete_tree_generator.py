from ete3 import NCBITaxa
import optparse


ncbi = NCBITaxa()

parser = optparse.OptionParser()
parser.add_option('-s', '--species', dest="input_species_filename",
                  help='Species list in text format one species in each line')

parser.add_option('-f', '--format', type='choice', choices=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '100'], dest="format",
                  default='8', help='outpur format for tree')

parser.add_option('-t', '--treebest', type='choice', choices=['yes', 'no'], dest="treebest",
                  default='no', help='To be used in TreeBest')

parser.add_option('-d', '--database', type='choice', choices=['yes', 'no'], dest="database",
                  default='no', help='Update database')

options, args = parser.parse_args()

if options.database == "yes":
    try:
        ncbi.update_taxonomy_database()
    except:
        pass

if options.input_species_filename is None:
    raise Exception('-s option must be specified, Species list in text format one species in each line')


with open(options.input_species_filename) as f:
    species_name = f.readlines()


for index, species in enumerate(species_name):
    species_name[index] = species.strip().replace("_", " ")


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

newickFile = open("newickTree.nhx", 'w')
newickFile.write(newickTree)
