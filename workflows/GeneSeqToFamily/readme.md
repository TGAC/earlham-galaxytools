# GeneSeqToFamily: the Ensembl GeneTrees pipeline as a Galaxy workflow


## Introduction

GeneSeqToFamily is an open-source Galaxy workflow based on the [Ensembl GeneTrees](http://www.ensembl.org/info/genome/compara/homology_method.html) pipeline. The Ensembl GeneTrees pipeline [1] infers the evolutionary history of gene families, represented as gene trees. It is a computational pipeline that comprises clustering, multiple sequence alignment, and tree generation (using [TreeBeST](http://treesoft.sourceforge.net/treebest.shtml)), to discover familial relationship.

## Workflow inputs and steps

### Inputs
GeneSeqToFamily requires the following inputs:

* The Coding Sequence (CDS)
* a species tree
* gene feature information in JSON format

### Steps

The pipeline is made up of 7 main steps:

1. Translation of CDS to protein sequences
2. All-vs-all BLASTP of protein sequences
3. Cluster protein sequences using [hcluster_sg](https://github.com/douglasgscofield/hcluster) and BLASTP scores
4. Multiple sequence alignment (MSA) for each cluster using [T-Coffee](http://www.tcoffee.org/Projects/tcoffee/)
5. Generate gene trees from MSAs using [TreeBeST](http://treesoft.sourceforge.net/treebest.shtml)
6. Create an SQLite database from the MSAs, gene trees and gene feature information using Gene Alignment and Family Aggregator (GAFA)
7. Visualise the GAFA dataset using Aequatus


### Helper tools:

We have developed various tools to help with data preparation for the workflow. This includes tools for retrieving sequences, and features from Ensembl using its REST API, and tools to parse Ensembl results into the required formats for the workflow. We also developed a tool to merge gene feature files and convert them from GFF3 (Gene Feature File) to JSON format, which is then used to generate the Aequatus dataset.


## Results

The resulting gene families can be visualised using the [Aequatus.js](https://github.com/TGAC/aequatus.js) interactive tool, which is developed as part of the [Aequatus software](https://github.com/TGAC/aequatus) [2].

The Aequatus.js plugin provides an interactive visual representation of the phylogenetic and structural relationships among the homologous genes, using a shared colour scheme for coding regions to represent homology in internal gene structure alongside their corresponding gene trees. It is also able to indicate insertions and deletions in homologous genes with respect to shared ancestors.

## List of tools
GeneSeqToFamily requires the following tools to run the workflow successfully:

* Transeq
* Filter by FASTA IDs
* BLAST
* BLAST parser
* hcluster_sg
* hcluster_sg parser
* T-Coffee
* Tranalign
* TreeBeST
* Gene Alignment and Family Aggregator (GAFA)

Some tools for data conversion during workflow:

* cut

Helper tools for data preparation:

* Ensembl REST API - tools for retrieving sequences, and features from Ensembl using its [REST API](http://rest.ensembl.org/)
* gff3-to-json - to merge gene feature files and convert them from GFF3 (Gene Feature File) to JSON format


## References

1. Vilella AJ, Severin J, Ureta-Vidal A, Heng L, Durbin R, Birney E (2009) [EnsemblCompara GeneTrees: Complete, duplication-aware phylogenetic trees in vertebrates.](http://genome.cshlp.org/content/19/2/327) *Genome Res.* 19(2):327–335, doi: 10.1101/gr.073585.107
2. Thanki AS, Ayling S, Herrero J, Davey RP (2016) [Aequatus: An open-source homology browser.](http://biorxiv.org/content/early/2016/06/01/055632) *bioRxiv*, doi: 10.1101/055632

## Project contacts:

* Anil Thanki <Anil.Thanki@earlham.ac.uk>
* Nicola Soranzo <Nicola.Soranzo@earlham.ac.uk>
* Robert Davey <Robert.Davey@earlham.ac.uk>

Copyright &copy; 2016 Earlham Institute, Norwich, UK
