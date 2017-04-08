# Script to run over-representation and gene set enrichment (GSE) analysis
# with KEGG for homo sapiens - using clusterProfiler package [Yu et al, 2012] 
# [Yu et al., 2012] Yu G, Wang L, Han Y and He Q (2012), clusterProfiler: an R package 
# for comparing biological themes among gene clusters.” OMICS: A Journal of Integrative Biology, 16(5), 
# pp. 284-287. doi: 10.1089/omi.2011.0118. 
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
# Inputs: 
#   File name            Tabular (txt) file with columns: (gene) name, value and ranking
#   Output directory     
# Outputs:
#   enrichment-KEGG.txt   list of over-represented categories with KEGG
#   enrichment-KEGG.pdf   figure with the first over-representated categories
#   gse-KEGG.txt          results for gse analysis
#
# It requieres R Packages:
# clusterProfiler, https://bioconductor.org/packages/release/bioc/html/clusterProfiler.html
# BBmisc
# org.Hs.eg.db
#
# To run script from a terminal use the command:
# Rscript enrichmentKEGG.R 'path-to-directory/file-name.txt' 'path-to-output-folder/'

# Input Arguments
args = commandArgs(trailingOnly=TRUE)

# User must provide at least an input file, and optionally the output directory 
if (length(args)==0) {
  stop("At least one argument must be supplied (input file).n", call.=FALSE)
} else if (length(args)==1) {
  # if no output file is provided, use current directory
  outputDir = "./"
} else if (length(args)==2) {
  outputDir <- args[2]
}

dataFile <- args[1]
cat(sprintf("Loading data from file: %s\n", dataFile))

if(!dir.exists(outputDir)){
  cat(sprintf("Creating output directory: %s\n", outputDir))
  dir.create(outputDir)
}

# Load file with data for analysis
data <- read.table(dataFile, header=TRUE, sep = "\t", stringsAsFactors=FALSE)
cat(sprintf("Number of genes: %i\n",nrow(data)))


library(clusterProfiler)
library(BBmisc)

D <- sortByCol(data, 'ranking')
D <- D[D[,2]!=0,]
D <- D[,c(1,2,3)]  # Only interested in the first three columns [name, value, ranking]
entrez<-bitr(D$name, fromType="SYMBOL", toType="ENTREZID", OrgDb="org.Hs.eg.db", drop = FALSE)
ranked<-merge(D,entrez,by.x='name',by.y='SYMBOL')
ranked <- sortByCol(ranked, 'ranking')
geneList <- ranked$value
names(geneList) <- ranked$ENTREZID

cat(sprintf("Performing over-representation analysis (with KEGG) ...  "))
cat(sprintf("Results saved to folder: %s\n", outputDir))


#### Enrichment with KEGG ####
enrichment_kegg <- enrichKEGG(ranked$ENTREZID, organism = 'hsa', keyType = "kegg")
results <- summary(enrichment_kegg)
head(results)


# modify column names for consistency with MultiPEN and for valid MATLAB identifiers
# change: pvalue to pValue, p.adjust to pAdjust, qvalue to qValue
aux <- colnames(results)
aux[c(5,6,7)] <- c("pValue", "pAdjust", "qValue")
colnames(results) <- aux

#write results (table) to file: 
fileName <- paste(outputDir, "enrichment-KEGG.txt", sep = "")
cat(sprintf("writing results to file: %s\n", fileName))
write.table(results, fileName, sep = '\t', row.names = FALSE)

# save plot to file:
fileName <- paste(outputDir, 'enrichment-KEGG.pdf', sep = "")
pdf(fileName)
barplot(enrichment_kegg, showCategory=20)


#### Gene Set Enrichment with KEGG ####
kk <- gseKEGG(geneList, organism = 'hsa', keyType = "kegg")
results <- summary(kk)
results


# modify column names for consistency for valid MATLAB identifiers
# change: p.adjust to pAdjust
aux <- colnames(results)
aux[c(6,7,8)] <- c("pValue", "pAdjust", "qValue")
colnames(results) <- aux

#write results (table) to file: 
fileName <- paste(outputDir, "gse-KEGG.txt", sep = "")
cat(sprintf("writing results to file: %s\n", fileName))
write.table(results, fileName, sep = '\t', row.names = FALSE)

# save plot to file (currently not supported!):
# fileName <- paste(outputDir, 'gse-KEGG.pdf', sep = "")
# pdf(fileName)
# barplot(kk)