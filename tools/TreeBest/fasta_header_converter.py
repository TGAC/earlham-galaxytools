import json

import optparse


transcript_species_dict = dict()
sequence_dict = dict()


def readgene(gene):
    for transcript in gene['Transcript']:
        transcript_species_dict[transcript['id']] = transcript['species'].replace("_", "")


def read_fasta(fp):
    for line in fp:
        line = line.rstrip()
        if line.startswith(">"):
            name = line.replace(">", "")
            print ">" + name + "_" + transcript_species_dict[name]
        else:
            print line


parser = optparse.OptionParser()
parser.add_option('-j', '--json', dest="input_gene_filename",
                  help='Gene Tree from Ensembl in JSON format')

parser.add_option('-f', '--fasta', dest="input_fasta_filename",
                  help='Gene Tree from Ensembl in JSON format')

options, args = parser.parse_args()

if options.input_gene_filename is None:
    raise Exception('-j option must be specified')

if options.input_fasta_filename is None:
    raise Exception('-f option must be specified')

with open(options.input_gene_filename) as data_file:
    data = json.load(data_file)

for gene_dict in data.values():
    readgene(gene_dict)

with open(options.input_fasta_filename) as fp:
    read_fasta(fp)
