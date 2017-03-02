from __future__ import print_function

import collections
import json
import optparse
import sys

Sequence = collections.namedtuple('Sequence', ['header', 'sequence'])


def FASTAReader_gen(fasta_filename):
    with open(fasta_filename) as fasta_file:
        line = fasta_file.readline()
        while True:
            if not line:
                return
            assert line.startswith('>'), "FASTA headers must start with >"
            header = line.rstrip()
            sequence_parts = []
            line = fasta_file.readline()
            while line and line[0] != '>':
                sequence_parts.append(line.rstrip())
                line = fasta_file.readline()
            sequence = "\n".join(sequence_parts)
            yield Sequence(header, sequence)


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
parser.add_option('-o', '--output', dest="output_fasta_filename",
                  help='Output FASTA file name')
options, args = parser.parse_args()

if options.input_gene_filename is None:
    raise Exception('-j option must be specified')
if options.input_fasta_filename is None:
    raise Exception('-f option must be specified')
if options.output_fasta_filename is None:
    raise Exception('-o option must be specified')

with open(options.input_gene_filename) as json_fh:
    gene_info = json.load(json_fh)
transcript_species_dict = read_gene_info(gene_info)

with open(options.output_fasta_filename, 'w') as output_fasta_file:
    for entry in FASTAReader_gen(options.input_fasta_filename):
        name = entry.header[1:].lstrip()
        if name not in transcript_species_dict:
            print("Transcript '%s' not found in the gene feature information" % name, file=sys.stderr)
            continue
        output_fasta_file.write(">%s_%s\n%s\n" % (name, transcript_species_dict[name], entry.sequence))
