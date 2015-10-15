# A simple tool to connect to the Ensembl server and retrieve sequences using
# the Ensembl REST API.
import json
import optparse
import requests
from urlparse import urljoin

server = "http://rest.ensembl.org"
ext = "sequence/id"

parser = optparse.OptionParser()
parser.add_option('-i', '--input', dest="input_filename",
                  help='List of Ensembl IDs')
parser.add_option('-t', '--type', type='choice',
                  choices=['genomic', 'cds', 'cdna', 'protein'],
                  default="genomic", help='Type of sequence')
parser.add_option('--expand_3prime', type='int', default=0,
                  help='Expand the sequence downstream of the sequence by this many basepairs. Only available when using genomic sequence type')
parser.add_option('--expand_5prime', type='int', default=0,
                  help='Expand the sequence upstream of the sequence by this many basepairs. Only available when using genomic sequence type')
parser.add_option('-f', '--format', type='choice', 
          choices=['json', 'fasta'],
          default="fasta", help='Output type, can be either JSON or Fasta')
options, args = parser.parse_args()
if options.input_filename is None:
    raise Exception('-i option must be specified')

if options.format == "json":
  headers = {"Content-Type": "application/json", "Accept": "application/json"}
elif options.format == "fasta": 
  headers = {"Content-Type": "text/x-fasta", "Accept": "text/x-fasta"}


params = dict((k, getattr(options, k)) for k in ['type', 'expand_3prime', 'expand_5prime'])
with open(options.input_filename) as f:
    ids = [line.strip() for line in f]
data = {'ids': ids}
r = requests.post(urljoin(server, ext), params=params, headers=headers,
                  data=json.dumps(data))

if not r.ok:
    r.raise_for_status()

print r.text
