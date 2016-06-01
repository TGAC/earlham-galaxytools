import json
import optparse

species = []


def speciesList(str):
    if not str['scientific_name'] in species:
        speciesFile.write(str['scientific_name'])
        species.append(str['scientific_name'])
        speciesFile.write("\n")


def geneLevel(str):
    if 'id' in str['sequence']:
        proteinLevel(str['sequence'])

    if 'taxonomy' in str:
        speciesList(str['taxonomy'])

    gene_file.write(str['id']['accession'])
    gene_file.write("\n")
    return


def proteinLevel(str):
    protein_file.write(str['id'][0]['accession'])
    protein_file.write("\t")
    protein_file.write(str['mol_seq']['cigar_line'])
    protein_file.write("\n")
    return


def recursiveGenes(str):
    children_len = len(data['tree']['children'])
    children_len -= 1
    children = str['children']

    while children_len >= 0:
        if 'sequence' in children[children_len]:
            geneLevel(children[children_len])
        else:
            recursiveGenes(children[children_len])
        children_len -= 1
    return


parser = optparse.OptionParser()
parser.add_option('-i', '--input', dest="input_filename",
    help='Gene Tree from Ensembl in JSON format')

options, args = parser.parse_args()

if options.input_filename is None:
    raise Exception('-i option must be specified')

with open(options.input_filename) as data_file:
    data = json.load(data_file)

children = data['tree']['children']
children_len = len(data['tree']['children'])
children_len -= 1

gene_file = open("gene.txt", 'w')
protein_file = open("protein.tabular", 'w')
speciesFile = open("species.txt", 'w')

while children_len >= 0:
    if 'sequence' in children[children_len]:
        geneLevel(children[children_len])
    else:
        recursiveGenes(children[children_len])

    children_len -= 1