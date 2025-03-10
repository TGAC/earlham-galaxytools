import optparse
from urllib.request import urlretrieve

from ete3.ncbi_taxonomy.ncbiquery import update_db

parser = optparse.OptionParser()
parser.add_option(
    "-t",
    "--taxdump",
    dest="taxdump",
    default=None,
    help="NCBI taxdump (tar.gz), will be downloaded if not given",
)
parser.add_option(
    "-d",
    "--database",
    dest="database",
    default=None,
    help="ETE sqlite data base to create",
)
options, args = parser.parse_args()
if options.database is None:
    parser.error("-d option must be specified")
if options.taxdump is not None:
    taxdump = options.taxdump
else:
    urlretrieve(
        "https://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz", "taxdump.tar.gz"
    )
    taxdump = "taxdump.tar.gz"

update_db(dbfile=options.database, targz_file=taxdump)
