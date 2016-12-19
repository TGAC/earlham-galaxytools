#!/usr/bin/env python
""" A script to build specific fasta databases """
from __future__ import print_function

import re
import sys


FASTA_MATCH_RE = re.compile(r'[^-]')


def convert_and_print(header, sequence):
    # Converts each match into M and each gap into D
    tmp_seq = FASTA_MATCH_RE.sub('M', sequence)
    tmp_seq = tmp_seq.replace('-', 'D')
    # Split the sequence in substrings composed by the same letter
    tmp_seq = tmp_seq.replace('DM', 'D,M')
    tmp_seq = tmp_seq.replace('MD', 'M,D')
    cigar_list = tmp_seq.split(',')
    # Condense each substring, e.g. DDDD in 4D, and concatenate them again
    cigar = ''
    for s in cigar_list:
        if len(s) > 1:
            cigar += str(len(s))
        cigar += s[0]
    print("%s\t%s" % (header, cigar))


def main():
    with open(sys.argv[1]) as fh:
        header = None
        sequence = None
        for line in fh:
            line = line.strip()
            if line and line[0] == '>':
                if header:
                    convert_and_print(header, sequence)
                header = line[1:]
                sequence = ''
            else:
                sequence += line
    if header:
        convert_and_print(header, sequence)


if __name__ == "__main__":
    main()
