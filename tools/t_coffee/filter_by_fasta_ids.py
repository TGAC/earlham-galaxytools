#!/usr/bin/env python
""" A script to build specific fasta databases """
from __future__ import print_function

import collections
import sys

Sequence = collections.namedtuple('Sequence', ['header', 'sequence'])


def FASTAReader_gen(fasta_filename):
    fasta_file = open(fasta_filename)
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
        sequence = "".join(sequence_parts)
        yield Sequence(header, sequence)


def target_match(target, search_entry):
    ''' Matches '''
    search_entry = search_entry.upper()
    for atarget in target:
        if search_entry.find(atarget) > -1:
            return atarget
    return None


def main():
    ''' the main function'''

    used_sequences = set()
    work_summary = {'wanted': 0, 'found': 0, 'duplicates': 0}
    targets = []

    with open(sys.argv[1]) as f_target:
        for line in f_target.readlines():
            targets.append(">%s" % line.strip().upper())

    work_summary['wanted'] = len(targets)

    # output = open(sys.argv[3], "w")
    for entry in FASTAReader_gen(sys.argv[2]):
        target_matched_results = target_match(targets, entry.header)
        if target_matched_results:
            work_summary['found'] += 1
            targets.remove(target_matched_results)
            sequence = entry.sequence
            used_sequences.add(sequence)
            print(entry.header)
            print(sequence)


if __name__ == "__main__":
    main()
