# A simple tool to connect to the Ensembl server and retrieve genetree using
# the Ensembl REST API.
import json
import optparse
import requests
from urlparse import urljoin

server = "http://rest.ensembl.org"


parser = optparse.OptionParser()
parser.add_option('-i', '--input', dest="input",
                  help='Ensembl ID')
parser.add_option('--nh_format', type='choice', default="simple",
                  choices=['full', 'display_label_composite', 'simple', 'species', 'species_short_name', 'ncbi_taxon', 'ncbi_name', 'njtree', 'phylip'],
                  help='The format of a NH (New Hampshire) request')
parser.add_option('-s', '--sequence', type='choice', 
                  choices=['none','cdna', 'protein'],
                  default="protein", help='The type of sequence to bring back. Setting it to none results in no sequence being returned')

parser.add_option('-c', '--cigar_line', type='choice', 
                  choices=['0','1'],
                  default="0", help='Return the aligned sequence encoded in CIGAR format')

parser.add_option('-a', '--aligned', type='choice', 
                  choices=['0','1'],
                  default="0", help='Return the aligned string if true. Otherwise, return the original sequence (no insertions)')
parser.add_option('--format', type='choice', default="json",
                  choices=['json', 'orthoxml', 'phyloxml', 'nh'],
                  help='Output format')

parser.add_option('--id_type', type='choice', default="gene_id",
                  choices=['gene_id', 'gene_tree_id'],
                  help='Input format')

options, args = parser.parse_args()

if options.input is None:
    raise Exception('-i option must be specified')


if options.id_type == "gene_id":
    ext = "/genetree/member/id/"
elif options.id_type == "gene_tree_id": 
    ext = "/genetree/id/"


if options.format == "json":
    headers = {"Content-Type": "application/json"}
elif options.format == "orthoxml": 
    headers = {"Content-Type": "text/x-orthoxml+xml"}
elif options.format == "phyloxml": 
    headers = {"Content-Type": "text/x-phyloxml+xml"}
elif options.format == "nh": 
    headers = {"Content-Type": "text/x-nh"}

params = dict((k, getattr(options, k)) for k in ['sequence', 'cigar_line', 'aligned', 'nh_format'])

r = requests.get(server+ext+options.input, params=params, headers=headers)

if not r.ok:
    r.raise_for_status()
    sys.exit()

print r.text
