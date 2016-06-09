GeneSeqToFamily
=================
Description: 
=================
GeneSeqToFamily: the Ensembl GeneTrees pipeline as a Galaxy workflow

© 2016. The Genome Analysis Centre, Norwich, UK

GeneSeqToFamily is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

GeneSeqToFamily is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with GeneSeqToFamily. If not, see http://www.gnu.org/licenses/.

#Input
Input for GeneSeqToFamily workflows are as below
* CDS sequences
* Species Tree
* Gene feature file in JSON format

#Required Tools
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

We have developed various tools to help with data preparation for the workflow:
* Ensembl REST API -  This includes tools for retrieving sequences, features and gene trees from Ensembl using its REST API, 
* Ensembl Parser - Tools to parse Ensembl results into the required format for workflow. 
* gff3-to-json - We also developed tool to merge gene feature files and convert them from GFF3 (Gene Feature File) to JSON format. 

# <a name="contacts"></a> Project contacts: 
* Anil Thanki <Anil.Thanki@tgac.ac.uk>
* Nicola Soranzo <Nicola.Soranzo@tgac.ac.uk>
* Robert Davey <Robert.Davey@tgac.ac.uk>
 

&copy; 2016. The Genome Analysis Centre, Norwich, UK
