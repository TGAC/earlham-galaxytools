# A simple tool to connect to the Ensembl server and retrieve feature
# information using the Ensembl REST API.
import json
import optparse
import requests
from urlparse import urljoin

server = "http://rest.ensembl.org"
ext = "lookup/id"

parser = optparse.OptionParser()
parser.add_option('-i', '--input', dest="input_filename",
                  help='List of Ensembl IDs')
parser.add_option('-e', '--expand', type='choice', choices=['0', '1'],
                  default="0",
                  help='Expands the search to include any connected features. e.g. If the object is a gene, its transcripts, translations and exons will be returned as well.')
parser.add_option('-f', '--format', type='choice',
                  choices=['full', 'condensed'], default="full",
                  help='Specify the formats to emit from this endpoint')
options, args = parser.parse_args()
if options.input_filename is None:
    raise Exception('-i option must be specified')

headers = {"Content-Type": "application/json", "Accept": "application/json"}
params = dict((k, getattr(options, k)) for k in ['format', 'expand'])
with open(options.input_filename) as f:
    ids = [line.strip() for line in f]
data = {'ids': ids}
r = requests.post(urljoin(server, ext), params=params, headers=headers,
                  data=json.dumps(data))

if not r.ok:
    r.raise_for_status()

print r.text
