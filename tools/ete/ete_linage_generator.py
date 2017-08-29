import optparse
import sys

from ete3 import NCBITaxa


# TODO: 
# - compared to gi2taxonomy the root is excluded, since 
#   the value is always "root", i.e. useless information
# - additional levels that appear in the ncbi taxdb have 
#   been added 
#   (order from https://en.wikipedia.org/wiki/Taxonomic_rank#All_ranks) 
# - could also be a parameter of the tool  
LONG_RANKS = [ u"superkingdom", u"kingdom", u"subkingdom", \
         u"superphylum", u"phylum", u"subphylum", \
         u"superclass", u"class", u"subclass", "infraclass", \
         u"cohort", \
         u"superorder", u"order", u"suborder", u"infraorder", u"parvorder", \
         u"superfamily", u"family", u"subfamily", \
         u"tribe", u"subtribe", \
         u"genus", u"subgenus", \
         u"species group", u"species subgroup" u"species", u"subspecies", \
         u"varietas", "forma" ]

SHORT_RANKS = [ u"kingdom", \
         u"phylum", \
         u"class", \
         u"order", \
         u"family", \
         u"genus", \
         u"species" ]

def process_taxid( ncbi, taxid, ranks, RANK_IDX, lower = False ):
    lineage = ncbi.get_lineage(taxid)
    lineage_ranks = ncbi.get_rank( lineage)
    lineage_names = ncbi.get_taxid_translator( lineage, try_synonyms=True)
    if lower: 
        lineage.reverse()
    for l in lineage:
        if not lineage_ranks[ l ] in RANK_IDX:
            continue
        if ranks[ RANK_IDX[ lineage_ranks[l] ] ] != "NA":
            continue
        ranks[ RANK_IDX[ lineage_ranks[l] ] ] = lineage_names[l]

ncbi = NCBITaxa()

parser = optparse.OptionParser()
parser.add_option('-s', '--species', dest="input_species_filename",
                  help='Species/taxid list in text format one species in each line')
parser.add_option('-d', '--database', type='choice', choices=['yes', 'no'], dest="database",
                  default='no', help='Update database')
parser.add_option('-r', '--ranks', type='choice', choices=['primary', 'full', 'compressed'], 
                  dest="ranks", default='compressed', help='Levels to show')
parser.add_option('-l', dest="lower", action = "store_true", default=False, help='Prefer lower levels when compressed')

parser.add_option('-o', '--output', dest="output", help='output file name')

options, args = parser.parse_args()

if options.database == "yes":
    try:
        ncbi.update_taxonomy_database()
    except:
        pass

if options.input_species_filename is None:
    raise Exception('-s option must be specified, Species list in text format one species in each line')

if options.ranks == "full":
    RANKS = LONG_RANKS
else:
    RANKS = SHORT_RANKS

RANK_IDX = {item : index for index, item in enumerate( RANKS )}
COMP_RANK_IDX = RANK_IDX
if options.ranks == "compressed":
    for ir in range( len(RANKS) ):
        for ilr in range( len( LONG_RANKS ) ):
            if RANKS[ir] in LONG_RANKS[ ilr ]:
                COMP_RANK_IDX[ LONG_RANKS[ ilr ] ] = ir 

of = open(options.output, "w")

with open(options.input_species_filename) as f:
    for line in f.readlines():
        line = line.strip().replace('_', ' ' )
        try:
            taxid = int( line )
        except ValueError:
# TODO: one could use fuzzy name lookup, but then a pysqlite version that
# supports this is needed (needs to be enabled during compilation)
            name2tax = ncbi.get_name_translator( [ line ] )
            if line in name2tax:
                taxid = name2tax[ line ][0]
            else:
                sys.stderr.write("[%s] could not be translated into a taxid!\n" %line )
                continue
        ranks = ["NA"] * len( RANKS )
        process_taxid( ncbi, taxid, ranks, RANK_IDX )
        if options.ranks == "compressed":
            process_taxid( ncbi, taxid, ranks, COMP_RANK_IDX, options.lower )
        of.write( "%s\t%s\n" %(line, "\t".join( ranks )  ))

of.close()
