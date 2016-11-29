#!/usr/bin/perl -w

# usage : perl script.pl <FASTA file> <method01> <method02> <method03> $dnd $msf_aln $clustalw_aln $pir_aln $fasta_aln $phylip $pir_seq $fasta_seq $score_ascii $score_html

#Chain wich will contains the paramater -output with the formats
my $outputFormat = "";
#Chain wich will contains the paramater for the -newtree, if the user wants
my $outputTree = "";
#Chain wich will contains the method of alignment of the process
my $total = "";
#Array where place the names of the formats, for the flag -output
my @formats = ("msf_aln", "clustalw_aln", "pir_aln", "fasta_aln", "phylip", "pir_seq", "fasta_seq", "score_ascii", "score_html");
#Array with the inputs for the methods of alignments
my @array = ($ARGV[1], $ARGV[2], $ARGV[3]);
#Array where will be placed the output files wich the user generate
my @files;

#Firstly the input methods of alignments are saved, if they exists (they aren't none), in the chain total, separated by commas
for (my $i = 0; $i < int(@array); $i++){
  if ($array[$i] ne "None"){
    $total.=$array[$i].",";
  } 
}

#If the user has selected the option of the tree, the chain of the tree will contains the file for the tree
if ($ARGV[4] ne "None") {
  $outputTree = "-newtree ".$ARGV[4]." ";
}

#copy is a variable which save the file and the extension of each output file ([0]:file1.dat, [1]:extension_file1, [2]:file2.dat, [3]extension_file2, ...)
my $copy = -1;
@array = ($ARGV[5],$ARGV[6],$ARGV[7],$ARGV[8],$ARGV[9],$ARGV[10],$ARGV[11],$ARGV[12],$ARGV[13]);
for (my $i = 0; $i < int(@array); $i++){
  if ($array[$i] ne "None"){
    $outputFormat.=$formats[$i].",";
    $copy++;
    $files[$copy]=$array[$i];
    $copy++;
    $files[$copy]=$formats[$i];
  } 
}

#if $total contains some method, we added the flag, and remove the last comma
if ($total ne "") {
  chop($total);
  $total = "-method ".$total;
}

#if $outputFormat contains some output, we added the flag, and remove the last comma
#the outfile will be the first output file
#tcoffee will generate a first file without extension, with the name indicated in -outfile, but the other files will be named like this first file and the extension of the format
if ($outputFormat ne "") {
  chop($outputFormat);
  $outputFormat = "-output ".$outputFormat." -outfile $files[0]";
}

#execution of the tcoffee; if there are not any method or output, this chains will be empty, so anything will be ejecuted in that flag
system("t_coffee $ARGV[0] $total $outputTree $outputFormat -quiet");

#finally, as tcoffee added an extension, we have to change the extension of the files and delete it (but not from the first file, that do not add any extension)
my $fi;
if ($copy > 1) {
  for (my $i = 2; $i < int(@files); $i+=2){
      $fi = $files[0].".".$files[$i+1];
     system ("mv $fi $files[$i]");
  }
}
