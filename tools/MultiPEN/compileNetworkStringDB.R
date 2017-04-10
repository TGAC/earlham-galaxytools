# Script to compile a Protein-Protein Interaction network using STRINGdb: 
# "STRINGdb (Search Tool for the Retrieval of Interacting proteins database)"
#    al. FAe (2013). “STRING v9.1: protein-protein interaction networks, with increased coverage and integration.” Nucleic Acids Research (Database issue), 41. 
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#Inputs: 
# fileName - table with column 'name'
# speciesCode = 9606  #homo sapiens
# threshold = minimum combined score
# networkFileName = "SI_network.human.NormalisedExpressionLevels.csv"
  
# It requieres R Packages:
# STRINGdb, http://bioconductor.org/packages/release/bioc/html/STRINGdb.html
#
# To run script from a terminal use the command:
# Rscript copileNetworkStringDB.R 'path-to-directory/fileName.txt' speciesCode threshold 'path-to-output-folder/networkFileName.txt'



# Input arguments
args = commandArgs(trailingOnly=TRUE)

# User must provide all four input parameters 
if (length(args)!=4) {
  stop("Please specify file name, species code, threshold and the name of the network", call.=FALSE)
}

fileName <- args[1]
speciesCode <- as.numeric(args[2]);
threshold <- as.numeric(args[3]);
networkFileName <- args[4];


# Read data, which needs to have at least the following two columns: [gene_id, shortName]
inputData <- read.delim( fileName, header = TRUE, sep = '\t', stringsAsFactors = FALSE)


#### begin compiling network ####
library(STRINGdb)
string_db <- STRINGdb$new( version="10", species = speciesCode, score_threshold=threshold, input_directory="" )
mapped <- string_db$map( inputData,  "name", removeUnmappedRows = TRUE )

#get interactions 
inter<-string_db$get_interactions(mapped$STRING_id)

#annotate source and target nodes
s <- paste(speciesCode, '.', sep = "")
from <- gsub(s, "", inter$from)
to <- gsub(s,"",inter$to)
#normalise combined_score values: divide by 1000
network <- data.frame(from = from, to = to, score = inter$combined_score/1000)
subNetwork <- network[network$score > threshold,] 

#edit STRING_id (speciesCode.ENSPxxxxx) to remove speciesCode
mapped$StringID <- gsub(s, "", mapped$STRING_id)
mapped$STRING_id <- NULL



#### network with gene names ####
nn <- dim(subNetwork)[1]
interactions <- matrix(data=NA,nrow=dim(subNetwork)[1], ncol=3)
for(ii in 1:nn){
  interactions[ii,1] = mapped$name[mapped$StringID==subNetwork$from[ii]]
  interactions[ii,2] = mapped$name[mapped$StringID==subNetwork$to[ii]]
  interactions[ii,3] = subNetwork$score[ii]
}

edges <- data.frame(source = interactions[,1], target = interactions[,2], score = interactions[,3])

#write two files to run with GenePEN
cat(sprintf('\nSaving network (edges) to file: %s', networkFileName))
cat('. . .')
#fileName <- paste(networkFileName, '.txt', sep = "")
write.table(edges, networkFileName, sep = '\t', col.names = T, row.names = FALSE, quote = FALSE)
cat(sprintf('Done!'))

