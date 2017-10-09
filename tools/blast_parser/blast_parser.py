"""
Simple parser to convert a BLAST 12-column or 24-column tabular output into a
3-column tabular input for hcluster_hg (id1, id2, weight):
"""
import argparse
import math
import sqlite3
import tempfile

BATCH_SIZE = 2000


def create_tables(conn):
    cur = conn.cursor()
    cur.execute('''CREATE TABLE alignment (
        id INTEGER PRIMARY KEY,
        sequence1_id VARCHAR NOT NULL,
        sequence2_id VARCHAR NOT NULL,
        weight INTEGER NOT NULL)''')
    conn.commit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', metavar='in-file', type=argparse.FileType('rt'), required=True, help='Path to input file')
    parser.add_argument('-o', metavar='out-file', type=argparse.FileType('wt'), required=True, help='Path to output file')
    parser.add_argument('-r', action='store_true', default=False,
                        dest='reciprocal',
                        help='Annotate homolog pair')
    options = parser.parse_args()

    db_file = tempfile.NamedTemporaryFile(suffix=".sqlite")

    conn = sqlite3.connect(db_file.name)
    conn.execute('PRAGMA foreign_keys = ON')

    create_tables(conn)

    cur = conn.cursor()

    i = 0
    for line in options.i:
        line = line.rstrip()
        line_cols = line.split('\t')
        sequence1_id = line_cols[0]
        sequence2_id = line_cols[1]

        # Ignore self-matching hits
        if sequence1_id == sequence2_id:
            continue

        i = i + 1
        evalue = float(line_cols[10])

        # Convert evalue to an integer weight with max 100
        if evalue != 0.0:
            weight = min(100, round(math.log10(evalue) / -2.0))
        else:
            # If the evalue is 0, leave weight at 100
            weight = 100

        cur.execute('INSERT INTO alignment (id, sequence1_id, sequence2_id, weight) VALUES (?, ?, ?, ?)',
                    (i, sequence1_id, sequence2_id, weight))

        # Commit transaction at every BATCH_SIZE rows to save memory
        if i % BATCH_SIZE == 0:
            conn.commit()
    # Commit final transaction
    conn.commit()
    options.i.close()

    # Delete alternative alignments keeping only one with max weight
    cur.execute('DELETE FROM alignment WHERE id NOT IN (SELECT id FROM alignment GROUP BY sequence1_id, sequence2_id HAVING weight=max(weight))')
    conn.commit()

    if options.reciprocal:
        query = 'SELECT a1.sequence1_id, a1.sequence2_id, a1.weight FROM alignment a1, alignment a2 WHERE a1.sequence1_id = a2.sequence2_id AND a1.sequence2_id = a2.sequence1_id ORDER BY a1.id'
    else:
        query = 'SELECT sequence1_id, sequence2_id, weight FROM alignment ORDER BY id'

    cur.execute(query)
    while True:
        rows = cur.fetchmany(BATCH_SIZE)
        if not rows:
            break
        for row in rows:
            options.o.write("%s\t%s\t%d\n" % row)

    conn.close()
    db_file.close()
    options.o.close()


if __name__ == "__main__":
    main()
