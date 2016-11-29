from __future__ import print_function

import optparse

parser = optparse.OptionParser()
parser.add_option('-s', '--strand', type='choice', choices=['D', 'R', 'both'],
                  default='D', help="Strand ('D', 'R' or 'both')")
options, args = parser.parse_args()
if len(args) != 2:
    parser.error('Specify 2 input file paths')


with open(args[1], 'r') as snpfile:
    snps = []
    for line in snpfile:
        cells = line.rstrip('\n').split('\t')
        snps.append((cells[0], int(cells[1])))

with open(args[0], 'r') as rsat_out_file:
    for line in rsat_out_file:
        line = line.rstrip('\n')
        if line.startswith('#'):
            continue
        cells = line.split('\t')
        ft_type = cells[1]
        strand = cells[3]
        if ft_type != 'site' or \
                (options.strand != 'both' and strand != options.strand):
            continue
        gene = cells[0]
        start = int(cells[4])
        stop = int(cells[5])
        if start * stop < 0:
            raise ValueError("start and stop have different sign in line: %s" %
                             line)
        if start < 0:
            seqrange = range(-stop, -start + 1)
        else:
            seqrange = range(start, stop + 1)
        for (snp, pos) in snps:
            if snp == gene and pos in seqrange:
                print(line)
                break
