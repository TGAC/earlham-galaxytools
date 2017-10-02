"""
Simple parser to convert a BLAST 12-column or 24-column tabular output into a
3-column tabular input for hcluster_hg (id1, id2, weight):
"""
import argparse
import math
from collections import OrderedDict


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', metavar='in-file', type=argparse.FileType('rt'), required=True, help='Path to input file')

    parser.add_argument('-o', metavar='out-file', type=argparse.FileType('wt'), required=True, help='Path to output file')

    parser.add_argument('-r', action='store_true', default=False,
                        dest='reciprocal',
                        help='Annotate homolog pair')

    parser.add_argument('--version', action='version', version='%(prog)s 1.0')

    options = parser.parse_args()

    results = OrderedDict()

    for line in options.i:
        line = line.rstrip()
        line_cols = line.split('\t')
        sequence1_id = line_cols[0]
        sequence2_id = line_cols[1]
        evalue = float(line_cols[10])

        # Ignore self-matching hits
        if sequence1_id != sequence2_id:
            # Convert evalue to an integer weight with max 100
            weight = 100

            # If the evalue is 0, leave weight at 100
            if evalue != 0.0:
                weight = min(100, round(math.log10(evalue) / -2.0))

            if (sequence1_id, sequence2_id) not in results:
                results[(sequence1_id, sequence2_id)] = weight
            else:
                results[(sequence1_id, sequence2_id)] = max(results[(sequence1_id, sequence2_id)], weight)

    for (sequence1_id, sequence2_id), weight in results.items():
        if not options.reciprocal or (sequence2_id, sequence1_id) in results:
            options.o.write("%s\t%s\t%d\n" % (sequence1_id, sequence2_id, weight))


if __name__ == "__main__":
    main()
