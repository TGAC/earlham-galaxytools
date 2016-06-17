GeneSeqToFamily: the Ensembl GeneTrees pipeline as a Galaxy workflow
=================


# Introduction 
 GeneSeqToFamily, an open-source Galaxy workflow based on the Ensembl GeneTrees pipeline. The Ensembl GeneTrees pipeline [1] infers the evolutionary history of gene families, represented as gene trees. It is a computational pipeline that comprises  clustering, multiple alignment, and tree generation (using TreeBeST), to discover familial relationship. 

# Workflow and inputs

## Input
GeneSeqToFamily requires the following inputs:
* CDS sequences
* A species tree
* Gene feature information in JSON format

## Workflow

The pipeline is made up of 7 main steps:
* Translation from CDS to protein sequences
* all-vs-all BLASTP of protein sequences
* Cluster sequences using hcluster_sg 
* Multiple sequence alignment (MSA) for each cluster using T-Coffee 
* Generate gene trees from MSAs using TreeBest
* Create Aequatus dataset from MSA, gene tree and gene feature information using Aequatus generator 
* Visualise Aequatus dataset


## Helper tools:
We have developed various tools to help with data preparation for the workflow. This includes tools for retrieving sequences, features and gene trees from Ensembl using its REST API, and tools to parse Ensembl results into the required formats for the workflow. We also developed a tool to merge gene feature files and convert them from GFF3 (Gene Feature File) to JSON format, which is then used to generate the Aequatus dataset.


# Result
Resulted gene families can be visualised using the Aequatus.js interactive tool, which is developed as part of the Aequatus software.

The Aequatus.js plugin provides an interactive visual representation of the phylogenetic and structural relationships among the homologous genes, using a shared colour scheme for coding regions to represent homology in internal gene structure alongside their corresponding gene trees. It is also able to indicate insertions and deletions in homologous genes with respect to shared ancestors.

# List of tools
GeneSeqToFamily requires the following tools to run workflow successfully:
* TranSeq
* filter fasta by ID
* BLAST
* BLAST parse
* hcluster_sg
* hcluster_sg parser
* T-Coffee
* TranAlign
* TreeBeST
* Aequatus generator

Some tools for data conversion during workflow:
* cut
* Fasta width
* Fasta to tabular

Helper tools for data preparation
Ensembl REST API - This includes tools for retrieving sequences, features and gene trees from Ensembl using its REST API,
Ensembl Parser - Tools to parse Ensembl results into the required format for workflow.
gff3-to-json - We also developed tool to merge gene feature files and convert them from GFF3 (Gene Feature File) to JSON format.


# Reference:
* Vilella AJ, Severin J, Ureta-Vidal A, Heng L, Durbin R, Birney E: EnsemblCompara GeneTrees: Complete, duplication-aware phylogenetic trees in vertebrates. Genome Res. 2009, 19(2):327–335. 
* Thanki AS, Ayling S, Herrero J, Davey RP: Aequatus: An open-source homology browser. bioRxiv 055632; doi: http://dx.doi.org/10.1101/055632

# <a name="contacts"></a> Project contacts: 
* Anil Thanki <Anil.Thanki@tgac.ac.uk>
* Nicola Soranzo <Nicola.Soranzo@tgac.ac.uk>
* Robert Davey <Robert.Davey@tgac.ac.uk>
 
# Licence
GeneSeqToFamily is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

GeneSeqToFamily is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with GeneSeqToFamily. If not, see http://www.gnu.org/licenses/.

&copy; 2016. The Genome Analysis Centre, Norwich, UK
