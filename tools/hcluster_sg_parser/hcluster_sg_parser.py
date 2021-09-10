"""
A simple parser to convert the hcluster_sg output into lists of IDs, one list for each cluster.

When a minimum and/or maximum number of cluster elements are specified, the IDs contained in the filtered-out clusters are collected in the "discarded IDS" output dataset.

Usage:

python hcluster_sg_parser.py [-m <N>] [-M <N>] <file> <discarded_out>
"""
import optparse
import os
import sys


def main():
    parser = optparse.OptionParser()
    parser.add_option('-m', '--min', type='int', default=0, help='Minimum number of cluster elements')
    parser.add_option('-M', '--max', type='int', default=sys.maxsize, help='Maximum number of cluster elements')
    parser.add_option('-d', '--dir', type='string', help="Absolute or relative path to output directory. If the directory does not exist, it will be created")
    options, args = parser.parse_args()

    if options.dir and not os.path.exists(options.dir):
        os.mkdir(options.dir)
    with open(args[2], 'w') as discarded_max_out:
        with open(args[1], 'w') as discarded_min_out:
            with open(args[0]) as fh:
                for line in fh:
                    line = line.rstrip()
                    line_cols = line.split('\t')
                    cluster_id = line_cols[0]
                    n_ids = int(line_cols[-2])
                    id_list = line_cols[-1].replace(',', '\n')
                    if n_ids < options.min:
                        discarded_min_out.write(id_list)
                    elif n_ids > options.max:
                        discarded_max_out.write(id_list)
                    else:
                        outfile = cluster_id + '_output.txt'
                        if options.dir:
                            outfile = os.path.join(options.dir, outfile)
                        with open(outfile, 'w') as f:
                            f.write(id_list)


if __name__ == "__main__":
    main()
