# A simple tool to connect to the Ensembl server and retrieve feature
# information using the Ensembl REST API.
import json
import optparse
from itertools import islice
from urllib.parse import urljoin

import requests

parser = optparse.OptionParser()
parser.add_option("-i", "--input", help="List of Ensembl IDs")
parser.add_option(
    "-e",
    "--expand",
    type="choice",
    choices=["0", "1"],
    default="0",
    help="Expands the search to include any connected features. e.g. If the object is a gene, its transcripts, translations and exons will be returned as well.",
)

parser.add_option(
    "-f",
    "--format",
    type="choice",
    choices=["full", "condensed"],
    default="full",
    help="Specify the formats to emit from this endpoint",
)
options, args = parser.parse_args()
if options.input is None:
    raise Exception("-i option must be specified")


server = "https://rest.ensembl.org"
ext = "lookup/id"

headers = {"Content-Type": "application/json", "Accept": "application/json"}
params = {k: getattr(options, k) for k in ("format", "expand")}

first = True

print("{")

with open(options.input) as f:
    while True:
        ids = [line.strip() for line in islice(f, 50)]
        if not ids:
            break
        if not first:
            print(",")
        data = {"ids": ids}
        r = requests.post(
            urljoin(server, ext),
            params=params,
            headers=headers,
            data=json.dumps(data),
            allow_redirects=False,
        )

        if not r.ok:
            r.raise_for_status()

        print(r.text[1:-1])

        first = False

print("}")
