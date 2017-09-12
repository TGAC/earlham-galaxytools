import optparse
import sys
# sys.path.append("./ete/")

import ete3

parser = optparse.OptionParser()
parser.add_option('-t', '--taxdump', dest='taxdump', default=None,
                  help='NCBI taxdump (tar.gz)')
parser.add_option('-d', '--database', dest="database", default=None,
                  help='ETE sqlite data base to use (default: ~/.etetoolkit/taxa.sqlite)')
options, args = parser.parse_args()
if options.database is None:
    parser.error("-d option must be specified")
if options.taxdump is not None:
    taxdump = options.database
else:
    from urllib import urlretrieve
    urlretrieve("http://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz", "taxdump.tar.gz")
    taxdump = "taxdump.tar.gz"

try:
    ete3.NCBITaxa(taxdump_file=taxdump, dbfile=options.database)
except TypeError:
    sys.stderr.write("ete_init_taxdb: outdated version of ete3")
    exit(1)
