# Script to run over-representation and gene set enrichment (GSE) analysis
# with Gene Ontology for homo sapiens - using clusterProfiler package [Yu et al, 2012] 
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
#   enrichment-GO.txt      list of over-represented categories with GO
#   enrichment-GO_BP.pdf   figure with the first over-representated biological processes terms
#   enrichment-GO_MF.pdf   figure with the first over-representated molecular functions terms
#   enrichment-GO_CC.pdf   figure with the first over-representated cellular components terms
#   gse-GO.txt             results for gse analysis
#
#
# It requieres R Packages:
# clusterProfiler, https://bioconductor.org/packages/release/bioc/html/clusterProfiler.html
# BBmisc
# GO.db
# org.Hs.eg.db
#
# To run from a terminal use following command:
# Rscript enrichmentGO.R '/path-to-file/file-name.txt' 'output-folder/'


# Input arguments
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
library(GO.db)

D <- sortByCol(data, 'ranking')
D <- D[,c(1,2,3)]  # Only interested in the first three columns [name, value, ranking]
entrez<-bitr(D$name, fromType="SYMBOL", toType="ENTREZID", OrgDb="org.Hs.eg.db", drop = FALSE)
ranked<-merge(D,entrez,by.x='name',by.y='SYMBOL')
ranked <- sortByCol(ranked, 'ranking')
geneList <- ranked$value
names(geneList) <- ranked$ENTREZID


#### Over-representation Analysis ####
cat(sprintf("Performing over-representation analysis (enrichGO) ...  "))
cat(sprintf("Results saved to folder: %s\n", outputDir))

#Enrichment for subontology BP (Biological Process)
subclassOnt <- "BP"
enrichment_BP <- enrichGO(ranked$ENTREZID, OrgDb="org.Hs.eg.db", ont=subclassOnt, readable=TRUE)
enrichmentSummary_BP <- as.data.frame(enrichment_BP)
head(enrichmentSummary_BP)
if(nrow(enrichmentSummary_BP)>0){
  aux <- cbind(enrichmentSummary_BP, "BP")
  colnames(aux)[10]<- 'subontology'
  enrichmentSummary_BP <- aux        
}  
#add to results: enrichment for BP category
results <- enrichmentSummary_BP

#Enrichment for subontology MF (Molecular Function)
subclassOnt <- "MF"
enrichment_MF <- enrichGO(ranked$ENTREZID, OrgDb="org.Hs.eg.db", ont=subclassOnt, readable=TRUE)
enrichmentSummary_MF <- as.data.frame(enrichment_MF)
head(enrichmentSummary_MF)
if(nrow(enrichmentSummary_MF)>0){
  aux <- cbind(enrichmentSummary_MF, "MF")
  colnames(aux)[10]<- 'subontology'
  enrichmentSummary_MF <- aux       
  #add to results: enrichment for MF category
  results <- rbind(results, enrichmentSummary_MF)
}  


#Enrichment for subclass CC (Cellular Component)
subclassOnt <- "CC"
enrichment_CC <- enrichGO(ranked$ENTREZID, OrgDb="org.Hs.eg.db", ont=subclassOnt, readable=TRUE)
enrichmentSummary_CC <- as.data.frame(enrichment_CC)
head(enrichmentSummary_CC)
if(nrow(enrichmentSummary_CC)>0){
  aux <- cbind(enrichmentSummary_CC, "CC")
  colnames(aux)[10]<- 'subontology'
  enrichmentSummary_CC <- aux
  #add to results: enrichment for CC category
  results <- rbind(results, enrichmentSummary_CC)
}

# modify column names for consistency with MultiPEN and for valid MATLAB identifiers
# change: pvalue to pValue, p.adjust to pAdjust, qvalue to qValue
aux <- colnames(results)
aux[c(5,6,7)] <- c("pValue", "pAdjust", "qValue")
colnames(results) <- aux

#write results to file: 
fileName <- paste(outputDir, "enrichment-GO.txt", sep = "")
cat(sprintf("writing results to file: %s\n", fileName))
write.table(results, fileName, sep = '\t', row.names = FALSE)


fileName <- paste(outputDir, 'enrichment-GO_BP.pdf', sep = "")
pdf(fileName)
barplot(enrichment_BP, showCategory=20)
dev.off()

fileName <- paste(outputDir, 'enrichment-GO_MF.pdf', sep = "")
pdf(fileName)
barplot(enrichment_MF, drop=TRUE, showCategory=20)
dev.off()

fileName <- paste(outputDir, 'enrichment-GO_CC.pdf', sep = "")
pdf(fileName)
barplot(enrichment_CC, showCategory=20)
dev.off()



#### Gene Set Enrichment Analysis ####
# GSE for all ontologies: BP, MF and CC
kk <- gseGO(geneList, ont = "ALL", OrgDb="org.Hs.eg.db", keytype = "ENTREZID")
results <- as.data.frame(kk)
results <- sortByCol(results, 'setSize', asc = F)
head(results)



# modify column names for consistency for valid MATLAB identifiers
# change: pvalue to pValue, p.adjust to pAdjust, qvalues to qValues
aux <- colnames(results)
aux[c(7,8,9)] <- c("pValue", "pAdjust", "qValue")
colnames(results) <- aux

#write results (table) to file: 
fileName <- paste(outputDir, "gse-GO.txt", sep = "")
cat(sprintf("writing results to file: %s\n", fileName))
write.table(results, fileName, sep = '\t', row.names = FALSE)

# save plot to file (currently not supported!):
# fileName <- paste(outputDir, 'gse-GO.pdf', sep = "")
# pdf(fileName)
# barplot(kk)
