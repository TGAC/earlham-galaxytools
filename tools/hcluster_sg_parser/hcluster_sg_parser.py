"""
A simple parser to convert the hcluster_sg 3-column output into lists of IDs, one list for each cluster.

When a minimum and/or maximum number of cluster elements are specified, the IDs contained in the filtered-out clusters are collected in the "discarded IDS" output dataset.

Usage:

python hcluster_sg_parser.py [-m <N>] [-M <N>] <file> <discarded_out>
"""
import optparse
import sys


def main():
    parser = optparse.OptionParser()
    parser.add_option('-m', '--min', type='int', default=0, help='Minimum number of cluster elements')
    parser.add_option('-M', '--max', type='int', default=sys.maxsize, help='Maximum number of cluster elements')
    options, args = parser.parse_args()

    with open(args[1], 'w') as discarded_out:
        with open(args[0]) as fh:
            for line in fh:
                line = line.rstrip()
                (cluster_id, n_ids, id_list) = line.split('\t')
                n_ids = int(n_ids)
                id_list = id_list.replace(',', '\n')
                if n_ids >= options.min and n_ids <= options.max:
                    outfile = cluster_id + '_output.txt'
                    with open(outfile, 'w') as f:
                        f.write(id_list)
                else:
                    discarded_out.write(id_list)


if __name__ == "__main__":
    main()
