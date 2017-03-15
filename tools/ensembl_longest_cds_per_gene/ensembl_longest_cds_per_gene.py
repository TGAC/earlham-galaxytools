"""
This script reads a CDS FASTA file from Ensembl and outputs a FASTA file with
only the longest CDS sequence for each gene.
"""
from __future__ import print_function

import collections
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


def remove_id_version(s):
    """
    Remove the optional '.VERSION' from an Ensembl id.
    """
    if s.startswith('ENS'):
        return s.split('.')[0]
    else:
        return s


parser = optparse.OptionParser()
parser.add_option('-f', '--fasta', dest="input_fasta_filename",
                  help='CDS file in FASTA format from Ensembl')
parser.add_option('-o', '--output', dest="output_fasta_filename",
                  help='Output FASTA file name')
options, args = parser.parse_args()

if options.input_fasta_filename is None:
    raise Exception('-f option must be specified')
if options.output_fasta_filename is None:
    raise Exception('-o option must be specified')

gene_transcripts_dict = dict()

for entry in FASTAReader_gen(options.input_fasta_filename):
    transcript_id, rest = entry.header[1:].split(' ', 1)
    gene_id = None
    for s in rest.split(' '):
        if s.startswith('gene:'):
            gene_id = remove_id_version(s[5:])
            break
    else:
        print("Gene id not found in header '%s'" % entry.header, file=sys.stderr)
        continue
    if gene_id in gene_transcripts_dict:
        gene_transcripts_dict[gene_id].append((transcript_id, len(entry.sequence)))
    else:
        gene_transcripts_dict[gene_id] = [(transcript_id, len(entry.sequence))]

# For each gene, select the transcript with the longest sequence
# If more than one transcripts have the same longest sequence for a gene, the
# first one to appear in the FASTA file is selected
selected_transcript_ids = [max(transcript_id_lengths, key=lambda _: _[1])[0] for transcript_id_lengths in gene_transcripts_dict.values()]

with open(options.output_fasta_filename, 'w') as output_fasta_file:
    for entry in FASTAReader_gen(options.input_fasta_filename):
        transcript_id = entry.header[1:].split(' ')[0]
        if transcript_id in selected_transcript_ids:
            output_fasta_file.write("%s\n%s\n" % (entry.header, entry.sequence))
