# getStringInteractome <- function(fileName, speciesCode, speciesName, networkFileName){
  # Get StringInteractome Network 
  
  # Load file with list of genes
  
  #INPUT 
  # fileName - table with column 'name'
  # speciesCode = 9606  #homo sapiens
  
  # networkFileName = "SI_network.human.NormalisedExpressionLevels.csv"
  

# Input arguments
args = commandArgs(trailingOnly=TRUE)

# User must provide at least an input file, and optionally the output directory 
length(args)
args
if (length(args)!=4) {
  stop("Please specify file name, species code, threshold and the name of the network", call.=FALSE)
}

fileName <- args[1]
class(args[2])
class(as.numeric(args[2]))
speciesCode <- as.numeric(args[2]);
threshold <- as.numeric(args[3]);
networkFileName <- args[4];


  # Read data, which needs to have at least the following two columns: [gene_id, shortName]
  inputData <- read.delim( fileName, header = TRUE, sep = '\t', stringsAsFactors = FALSE)
  #geneList <- inputData$name
  
  # begin compiling network
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
  
  # end compiling network
  
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
  
  
  #write.table(mapped, '~/Desktop/temp/mapped.txt', sep = '\t', col.names = T, row.names = FALSE, quote = FALSE)
  #write.table(subNetwork, '~/Desktop/temp/subnetwork.txt', sep = '\t', col.names = T, row.names = FALSE, quote = FALSE)
#}


