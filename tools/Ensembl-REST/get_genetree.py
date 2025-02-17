# A simple tool to connect to the Ensembl server and retrieve genetree using
# the Ensembl REST API.
import optparse
from urllib.parse import urljoin

import requests

parser = optparse.OptionParser()
parser.add_option(
    "--id_type",
    type="choice",
    default="gene_id",
    choices=["gene_id", "gene_tree_id"],
    help="Input type",
)
parser.add_option("--species", help="Species name/alias")
parser.add_option("-i", "--input", help="Ensembl ID")
parser.add_option(
    "--format",
    type="choice",
    choices=["json", "orthoxml", "phyloxml", "nh"],
    default="json",
    help="Output format",
)
parser.add_option(
    "-s",
    "--sequence",
    type="choice",
    choices=["protein", "cdna", "none"],
    default="protein",
    help="The type of sequence to bring back. Setting it to none results in no sequence being returned",
)

parser.add_option(
    "-a",
    "--aligned",
    type="choice",
    choices=["0", "1"],
    default="0",
    help="Return the aligned string if true. Otherwise, return the original sequence (no insertions)",
)
parser.add_option(
    "-c",
    "--cigar_line",
    type="choice",
    choices=["0", "1"],
    default="0",
    help="Return the aligned sequence encoded in CIGAR format",
)
parser.add_option(
    "--nh_format",
    type="choice",
    choices=[
        "full",
        "display_label_composite",
        "simple",
        "species",
        "species_short_name",
        "ncbi_taxon",
        "ncbi_name",
        "njtree",
        "phylip",
    ],
    default="simple",
    help="The format of a NH (New Hampshire) request",
)
options, args = parser.parse_args()
if options.input is None:
    raise Exception("-i option must be specified")

server = "https://rest.ensembl.org"

if options.id_type == "gene_id":
    ext = f"genetree/member/id/{options.species}/{options.input}"
elif options.id_type == "gene_tree_id":
    ext = f"genetree/id/{options.input}"

if options.format == "json":
    content_type = "application/json"
elif options.format == "orthoxml":
    content_type = "text/x-orthoxml+xml"
elif options.format == "phyloxml":
    content_type = "text/x-phyloxml+xml"
elif options.format == "nh":
    content_type = "text/x-nh"
headers = {"Content-Type": content_type}
params = {
    k: getattr(options, k) for k in ("sequence", "aligned", "cigar_line", "nh_format")
}
r = requests.get(urljoin(server, ext), params=params, headers=headers)

if not r.ok:
    r.raise_for_status()

print(r.text)
