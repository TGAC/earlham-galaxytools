import optparse
import sys

from ete3 import NCBITaxa

# - compared to gi2taxonomy the root is excluded, since
#   the value is always "root", i.e. useless information
# - additional levels that appear in the ncbi taxdb have
#   been added
#   (order from https://en.wikipedia.org/wiki/Taxonomic_rank#All_ranks)
# TODO the full list of ranks could be derived from the input DB
LONG_RANKS = [u"superkingdom", u"kingdom", u"subkingdom",
              u"superphylum", u"phylum", u"subphylum",
              u"superclass", u"class", u"subclass", "infraclass",
              u"cohort",
              u"superorder", u"order", u"suborder", u"infraorder", u"parvorder",
              u"superfamily", u"family", u"subfamily",
              u"tribe", u"subtribe",
              u"genus", u"subgenus",
              u"species group", u"species subgroup", u"species", u"subspecies",
              u"varietas", "forma"]

SHORT_RANKS = [u"kingdom",
               u"phylum",
               u"class",
               u"order",
               u"family",
               u"genus",
               u"species"]


def process_taxid(ncbi, taxid, ranks, RANK_IDX, lower=False):
    """
    process one taxid:
        - get lineage (as list of taxids, ranks, and names)
        - reverse the lineage if lower ranks are to be used for filling
        - fill the ranks with the data from the lineage
    ncbi: ete NCBITaxa object
    taxid: a taxid (int)
    ranks: list of ranks (should be initialized with "NA" x number of levels of interest)
    RANK_IDX: mapping from rank names to indices (distance to root/leaf?)
    lower: use lower taxa for filling "NA"s
    """
    lineage = ncbi.get_lineage(taxid)
    lineage_ranks = ncbi.get_rank(lineage)
    lineage_names = ncbi.get_taxid_translator(lineage, try_synonyms=True)
    if lower:
        lineage.reverse()
    for l in lineage:
        if not lineage_ranks[l] in RANK_IDX:
            continue
        if ranks[RANK_IDX[lineage_ranks[l]]] != "NA":
            continue
        ranks[RANK_IDX[lineage_ranks[l]]] = lineage_names[l]


# get command line options
parser = optparse.OptionParser()
parser.add_option('-s', '--species', dest="input_species_filename",
                  help='Species/taxid list in text format one species in each line')
parser.add_option('-d', '--database', dest="database", default=None,
                  help='ETE sqlite data base to use (default: ~/.etetoolkit/taxa.sqlite)')
parser.add_option('-o', '--output', dest="output", help='output file name (default: stdout)')
parser.add_option('-f', dest="full", action="store_true", default=False,
                  help='Show all available (named) taxonomic ranks (default: only primary levels)')
parser.add_option('-c', dest="compress", action="store_true", default=False,
                  help='Fill unnamed ranks with super/sub ranks (see -l)')
parser.add_option('-l', dest="lower", action="store_true", default=False,
                  help='Prefer lower levels when compressed')
parser.add_option('-r', '--rank', dest='ranks', action="append",
                  help='include rank - multiple ones can be specified')

options, args = parser.parse_args()
# check command line options
if options.input_species_filename is None:
    parser.error("-s option must be specified, Species list in text format one species in each line")
if options.full and options.ranks:
    parser.error("-f and -r can not be used at the same time")

if options.ranks:
    for r in options.ranks:
        if r not in LONG_RANKS:
            parser.error("unknown rank %s" % r)
# setup output
if not options.output:   # if filename is not given
    of = sys.stdout
else:
    of = open(options.output, "w")
# load NCBI taxonomy DB
ncbi = NCBITaxa(dbfile=options.database)
# get list of ranks that are of interest
if options.ranks:
    RANKS = []
    for r in LONG_RANKS:
        if r in options.ranks:
            RANKS.append(r)
else:
    if options.full:
        RANKS = LONG_RANKS
    else:
        RANKS = SHORT_RANKS
RANK_IDX = {item: index for index, item in enumerate(RANKS)}
COMP_RANK_IDX = RANK_IDX
if options.compress:
    for ir in range(len(RANKS)):
        for ilr in range(len(LONG_RANKS)):
            if RANKS[ir] in LONG_RANKS[ilr]:
                COMP_RANK_IDX[LONG_RANKS[ilr]] = ir
# write header
of.write("species/taxid\t%s\n" % ("\t".join(RANKS)))
# get and write data
with open(options.input_species_filename) as f:
    for line in f.readlines():
        line = line.strip().replace('_', ' ')
        try:
            taxid = int(line)
        except ValueError:
            # TODO: one could use fuzzy name lookup (i.e. accept typos in the species names),
            # but then a pysqlite version that supports this is needed (needs to be enabled
            # during compilation)
            name2tax = ncbi.get_name_translator([line])
            if line in name2tax:
                taxid = name2tax[line][0]
            else:
                sys.stderr.write("[%s] could not be translated into a taxid!\n" % line)
                continue
        ranks = ["NA"] * len(RANKS)
        process_taxid(ncbi, taxid, ranks, RANK_IDX)
        if options.compress:
            process_taxid(ncbi, taxid, ranks, COMP_RANK_IDX, options.lower)
        of.write("%s\t%s\n" % (line, "\t".join(ranks)))
of.close()
