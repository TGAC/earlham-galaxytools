#!/usr/bin/env Rscript

args <- commandArgs(TRUE)
countDataPath <- args[1]
statsDataPath <- args[2]
logFC <- args[3]
logCPM <- args[4]
pValue <- args[5]
fdr <- args[6]

clusterRow <- args[7]
clusterCol <- args[8]
hclustMethod <- args[9]

mgColumnNm <- as.numeric(args[10])
mgRowNm <- as.numeric(args[11])

pdfWidth <- as.numeric(args[12])
pdfHeight <- as.numeric(args[13])


if (clusterRow == "Yes") {
    clusterRow <- TRUE
} else {
    clusterRow <- NA
}

if (clusterCol == "Yes") {
    clusterCol <- TRUE
} else {
    clusterCol <- NA
}

require(preprocessCore)
require(gplots)

# prepare counts data --------------------------------------------------------
countData <- read.table(countDataPath,
    comment = "",
    sep = "\t"
)

groups <- sapply(as.character(countData[1, -1]), strsplit, ":")
groups <- as.vector(t(countData[1, -1]))

names <- as.vector(t(countData[2, -1]))

countData <- countData[-c(1, 2), ]
rownames(countData) <- countData[, 1]
countData <- countData[, -1]
colnames(countData) <- names

countData <- countData[, order(groups, names)]

# prepare stats data ------------------------------------------------------

statsData <- read.table(statsDataPath,
    sep = "\t",
    header = T
)

colnames(statsData)[-1] <- sapply(colnames(statsData)[-1], function(x) {
    unlist(strsplit(x, ".", fixed = T))[3]
})

wh <- which(abs(statsData$logFC) >= logFC & statsData$logCPM >= logCPM & statsData$PValue <= pValue & statsData$FDR <= fdr)

for (i in 1:ncol(countData)) {
    countData[, i] <- as.numeric(countData[, i])
}

countDataNorm <- normalize.quantiles(as.matrix(countData), copy = T)
countDataNormLog <- log(countDataNorm + 1, 2)

colnames(countDataNormLog) <- colnames(countData)
rownames(countDataNormLog) <- rownames(countData)

# svg("heatmap.svg", width = 3+length(names), height = 1/2*length(wh))
pdf("heatmap.pdf", width = pdfWidth, height = pdfHeight)

heatmap.2(
    countDataNormLog[wh, ],
    density.info = c("none"),
    hclustfun = function(x) hclust(x, method = hclustMethod),
    distfun = function(x) as.dist(1 - cor(t(x))),
    col = bluered(50),
    scale = "row",
    trace = "none",
    Rowv = clusterRow,
    Colv = clusterCol,
    margins = c(mgColumnNm, mgRowNm)
)

dev.off()
