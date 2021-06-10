# A simple tool to connect to the Ensembl server and retrieve sequences using
# the Ensembl REST API.
from __future__ import print_function

import json
import optparse
from itertools import islice

import requests
from six.moves.urllib.parse import urljoin

parser = optparse.OptionParser()
parser.add_option('-i', '--input', help='List of Ensembl IDs')

parser.add_option('-t', '--type', type='choice',
                  choices=['genomic', 'cds', 'cdna', 'protein'],
                  default='genomic', help='Type of sequence')
parser.add_option('--expand_3prime', type='int', default=0,
                  help='Expand the sequence downstream of the sequence by this many basepairs. Only available when using genomic sequence type')
parser.add_option('--expand_5prime', type='int', default=0,
                  help='Expand the sequence upstream of the sequence by this many basepairs. Only available when using genomic sequence type')
options, args = parser.parse_args()
if options.input is None:
    raise Exception('-i option must be specified')

server = 'https://rest.ensembl.org'
ext = 'sequence/id'

headers = {'Content-Type': 'text/x-fasta', 'Accept': 'text/x-fasta'}
params = dict((k, getattr(options, k)) for k in ['type', 'expand_3prime', 'expand_5prime'])
with open(options.input) as f:
    # Need to split the file in chunks of 50 lines because of the limit imposed by Ensembl
    while True:
        ids = [line.strip() for line in islice(f, 50)]
        if not ids:
            break
        data = {'ids': ids}
        r = requests.post(urljoin(server, ext), params=params, headers=headers,
                          data=json.dumps(data), allow_redirects=False)

        if not r.ok:
            r.raise_for_status()

        print(r.text)
