"""
Simple parser to convert a BLAST 12-column or 24-column tabular output into a
3-column tabular input for hcluster_hg (id1, id2, weight):
"""
import argparse
import math
import sqlite3


def create_tables(conn):
    cur = conn.cursor()
    cur.execute('''CREATE TABLE homology (
        homology_id INTEGER NOT NULL,
        sequence1_id VARCHAR NOT NULL,
        sequence2_id VARCHAR NOT NULL,
        weight INT NOT NULL)''')
    conn.commit()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', metavar='in-file', type=argparse.FileType('rt'), required=True, help='Path to input file')

    parser.add_argument('-o', metavar='out-file', type=argparse.FileType('wt'), required=True, help='Path to output file')

    parser.add_argument('-r', action='store_true', default=False,
                        dest='reciprocal',
                        help='Annotate homolog pair')

    parser.add_argument('--version', action='version', version='%(prog)s 1.0')

    options = parser.parse_args()

    db_name = options.o.name.split(".")[0] + ".sqlite"

    conn = sqlite3.connect(db_name)
    conn.execute('PRAGMA foreign_keys = ON')

    create_tables(conn)

    i = 0

    cur = conn.cursor()

    for line in options.i:
        line = line.rstrip()
        line_cols = line.split('\t')
        sequence1_id = line_cols[0]
        sequence2_id = line_cols[1]
        evalue = float(line_cols[10])

        # Ignore self-matching hits
        if sequence1_id != sequence2_id:
            i = i + 1

            # Convert evalue to an integer weight with max 100
            weight = 100

            # If the evalue is 0, leave weight at 100
            if evalue != 0.0:
                weight = min(100, round(math.log10(evalue) / -2.0))

            # Insert pair into SQLite database
            cur.execute('INSERT INTO homology (homology_id, sequence1_id, sequence2_id, weight) VALUES (?, ?, ?, ?)',
                        (i, sequence1_id, sequence2_id, weight))

            # Execute query at every 100 pair to save memory
            if(i % 100 == 0):
                conn.commit()

    # Execute query at last
    conn.commit()

    # Delete duplicate keeping one with max weight
    cur.execute('delete FROM homology WHERE homology_id  IN (SELECT a1.homology_id FROM homology a1 INNER JOIN homology a2 ON a1.sequence1_id = a2.sequence1_id AND a1.sequence2_id = a2.sequence2_id AND a1.weight < a2.weight)')

    # Execute delete query
    conn.commit()

    # General select query
    query = 'SELECT * FROM homology ORDER BY homology_id'

    # Update select query if reciprocal selected
    if options.reciprocal:
        query = 'SELECT h1.* FROM homology h1, homology h2 WHERE h1.sequence1_id =  h2.sequence2_id AND h1.sequence2_id =  h2.sequence1_id ORDER BY h1.homology_id'

    cur.execute(query)
    results = cur.fetchall()
    for result in results:
        options.o.write("%s\t%s\t%d\n" % (result[1], result[2], result[3]))


if __name__ == "__main__":
    main()
