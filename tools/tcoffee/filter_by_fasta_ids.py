#!/usr/bin/env python
""" A script to build specific fasta databases """
from __future__ import print_function
import sys
import logging


# ===================================== Iterator ===============================
class Sequence:
    ''' Holds protein sequence information '''
    def __init__(self):
        self.header = ""
        self.sequence_parts = []

    def get_sequence(self):
        return "".join([line.rstrip().replace('\n', '').replace('\r', '') for line in self.sequence_parts])


class FASTAReader:
    """
        FASTA db iterator. Returns a single FASTA sequence object.
    """
    def __init__(self, fasta_name):
        self.fasta_file = open(fasta_name)
        self.next_line = self.fasta_file.readline()

    def __iter__(self):
        return self

    def __next__(self):
        ''' Iteration '''
        # while True:
        #    line = self.fasta_file.readline()
        #    if not line:
        #        raise StopIteration
        #    if line[0] == '>':
        #        break
        next_line = self.next_line
        if not next_line:
            raise StopIteration

        seq = Sequence()
        seq.header = next_line.rstrip().replace('\n', '').replace('\r', '')

        next_line = self.fasta_file.readline()
        while next_line and next_line[0] != '>':
            # tail = self.fasta_file.tell()
            # line = self.fasta_file.readline()
            # if not line:
            #   break
            # if line[0] == '>':
            #   self.fasta_file.seek(tail)
            #   break
            seq.sequence_parts.append(next_line)
            next_line = self.fasta_file.readline()
        self.next_line = next_line
        return seq

    # Python 2/3 compat
    next = __next__
# ==============================================================================


def target_match(target, search_entry):
    ''' Matches '''
    search_entry = search_entry.upper()
    for atarget in target:
        if search_entry.find(atarget) > -1:
            return atarget
    return None


def main():
    ''' the main function'''
    logging.basicConfig(filename='filter_fasta_log',
                        level=logging.INFO,
                        format='%(asctime)s :: %(levelname)s :: %(message)s',)

    used_sequences = set()
    work_summary = {'wanted': 0, 'found': 0, 'duplicates': 0}
    targets = []

    f_target = open(sys.argv[1])
    for line in f_target.readlines():
        targets.append(">%s" % line.strip().upper())
    f_target.close()

    work_summary['wanted'] = len(targets)
    homd_db = FASTAReader(sys.argv[2])

    # output = open(sys.argv[3], "w")
    for entry in homd_db:
        target_matched_results = target_match(targets, entry.header)
        if target_matched_results:
            work_summary['found'] += 1
            targets.remove(target_matched_results)
            sequence = entry.get_sequence()
            used_sequences.add(sequence)
            print(entry.header)
            print(sequence)
    for parm, count in work_summary.items():
        logging.info('%s ==> %d', parm, count)


if __name__ == "__main__":
    main()
