import sys
sys.path.append("./ete/")

import ete3

ete3.NCBITaxa(taxdump_file="/tmp/taxdump/taxdump.tar.gz", dbfile="taxdump.sqlite")
