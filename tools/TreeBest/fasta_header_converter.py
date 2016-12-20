from __future__ import print_function

import json
import optparse


def read_gene_info(gene_info):
    transcript_species_dict = dict()
    for gene_dict in gene_info.values():
        for transcript in gene_dict['Transcript']:
            transcript_species_dict[transcript['id']] = transcript['species'].replace("_", "")
    return transcript_species_dict


parser = optparse.OptionParser()
parser.add_option('-j', '--json', dest="input_gene_filename",
                  help='Gene feature information in JSON format')
parser.add_option('-f', '--fasta', dest="input_fasta_filename",
                  help='Sequences in FASTA format')
options, args = parser.parse_args()

if options.input_gene_filename is None:
    raise Exception('-j option must be specified')

if options.input_fasta_filename is None:
    raise Exception('-f option must be specified')

with open(options.input_gene_filename) as json_fh:
    gene_info = json.load(json_fh)
transcript_species_dict = read_gene_info(gene_info)

with open(options.input_fasta_filename) as fasta_fh:
    for line in fasta_fh:
        line = line.rstrip()
        if line.startswith(">"):
            name = line[1:].lstrip()
            print(">" + name + "_" + transcript_species_dict[name])
        else:
            print(line)
