import optparse

import ete3.ncbi_taxonomy
from six.moves.urllib.request import urlretrieve

parser = optparse.OptionParser()
parser.add_option('-t', '--taxdump', dest='taxdump', default=None,
                  help='NCBI taxdump (tar.gz) will be downloaded if not given')
parser.add_option('-d', '--database', dest="database", default=None,
                  help='ETE sqlite data base to use (default: ~/.etetoolkit/taxa.sqlite)')
options, args = parser.parse_args()
if options.database is None:
    parser.error("-d option must be specified")
if options.taxdump is not None:
    taxdump = options.taxdump
else:
    urlretrieve("http://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz", "taxdump.tar.gz")
    taxdump = "taxdump.tar.gz"

# will remove a taxdump.tar.gz file at the end
# which will lead to an errmessage if not present
# if the tool is run on a taxdump in the current dir it will be
# deleted in the end
ete3.ncbi_taxonomy.ncbiquery.update_db(dbfile=options.database, targz_file=taxdump)
