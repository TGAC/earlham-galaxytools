"""
A simple parser to convert the hcluster_sg 3-column output into lists of IDs, one list for each cluster. Usage:

python hcluster_sg_parser.py <file>
"""
import sys


def main():
    with open(sys.argv[1]) as fh:
        for line in fh:
            line = line.rstrip()
            (cluster_id, n_ids, id_list) = line.split('\t')
            id_list = id_list.replace(',', '\n')
            outfile = cluster_id + '_output.txt'
            with open(outfile, 'w') as f:
                f.write(id_list)


if __name__ == "__main__":
    main()
