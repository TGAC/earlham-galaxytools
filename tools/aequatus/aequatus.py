from __future__ import print_function
import json
import optparse
import sqlite3

version = "0.2.0"


def create_table(conn):
    conn.execute('''CREATE TABLE gene_family
       (gene_family_id INT NOT NULL,
       gene_id INT KEY NOT NULL,
       protein_id INT KEY NOT NULL,
       alignment VARCHAR NOT NULL);''')

    conn.execute('''CREATE TABLE gene_tree
       (gene_family_id INT PRIMARY KEY NOT NULL,
       gene_tree VARCHAR NOT NULL);''')

    conn.execute('''CREATE TABLE gene_information
       (gene_id VARCHAR PRIMARY KEY NOT NULL,
       gene_json VARCHAR NOT NULL);''')


def cigar_to_db(conn, i, fname, gene_dict):
    cigar_dict = dict()
    matched_gene_ids = set()
    with open(fname) as f:
        for element in f.readlines():
            seq_id, cigar = element.rstrip('\n').split('\t')
            (protein_id, gene_id) = get_protein_and_gene_id_from_seq_id(gene_dict, seq_id)
            cigar_dict[protein_id] = cigar

            conn.execute("INSERT INTO gene_family (gene_family_id, gene_id, protein_id, alignment) \
                VALUES (?,?,?,?) ", (i, gene_id, protein_id, cigar))

            conn.commit()
            matched_gene_ids.add(gene_id)
    return cigar_dict, matched_gene_ids


def newicktree_to_db(conn, i, fname):
    tree = ""
    with open(fname) as f:
        tree = f.read().replace('\n', '')

    conn.execute("INSERT INTO gene_tree (gene_family_id, gene_tree) \
                VALUES (?,?) ", (i, tree))
    conn.commit()


def gene_json_to_dict(fname):

    with open(fname) as f:
        return json.load(f)


def gene_json_to_db(conn, fname):
    gene = dict()

    with open(fname) as f:
        gene = json.load(f)

    for key, value in gene.iteritems():
        conn.execute("INSERT INTO gene_information (gene_id, gene_json) \
                VALUES (?,?) ", (key, json.dumps(value)))

    conn.commit()


def get_protein_and_gene_id_from_seq_id(gene_dict, seq_id):
    """
    Search inside gene_dict for a gene having a transcript id or protein id
    equal to seq_id. Returns the protein id and the gene id.
    """
    for gene in gene_dict.values():
        if "Transcript" in gene:
            for transcript in gene["Transcript"]:
                if transcript['id'] == seq_id:
                    if 'Translation' in transcript and 'id' in transcript['Translation']:
                        return transcript["Translation"]["id"], gene['id']
                    else:
                        break
                elif 'Translation' in transcript and 'id' in transcript['Translation'] and transcript["Translation"]["id"] == seq_id:
                    return seq_id, gene['id']


def __main__():
    parser = optparse.OptionParser()
    parser.add_option('-t', '--tree', action='append', help='Gene tree files')
    parser.add_option('-c', '--cigar', action='append', help='CIGAR alignments of CDS files in tabular format')
    parser.add_option('-g', '--gene', help='Gene features file in JSON format')
    parser.add_option('-s', '--sort', action='store_true', help='Sort the keys in the JSON output')
    parser.add_option('-o', '--output', help='Path of the output file. If not specified, will print on the standard output')
    options, args = parser.parse_args()
    if args:
        raise Exception('Use options to provide inputs')

    conn = sqlite3.connect(options.output)

    create_table(conn)

    gene_dict = gene_json_to_dict(options.gene)

    gene_json_to_db(conn, options.gene)

    i = 1
    for tree, cigar in zip(options.tree, options.cigar):
        cigar_to_db(conn, i, cigar, gene_dict)
        newicktree_to_db(conn, i, tree)
        i += 1

if __name__ == '__main__':
    __main__()
