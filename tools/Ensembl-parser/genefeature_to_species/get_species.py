import json
import optparse

species = []


def readgene(gene):
    for transcript in gene['Transcript']:
        species.append(transcript['species'])

parser = optparse.OptionParser()
parser.add_option('-j', '--json', dest="input_gene_filename",
                  help='Gene Tree from Ensembl in JSON format')

options, args = parser.parse_args()

if options.input_gene_filename is None:
    raise Exception('-j option must be specified')

with open(options.input_gene_filename) as data_file:
    data = json.load(data_file)

for gene_dict in data.itervalues():
    readgene(gene_dict)

print "\n".join(list(set(species)))
