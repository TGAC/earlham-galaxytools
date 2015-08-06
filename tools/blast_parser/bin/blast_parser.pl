#!/usr/bin/perl
#
use strict;
use warnings;
use List::Util qw[min max];

#A simple perl parser to convert BLAST 12 column output onto 3 column input for hcluster_hg (id1, id2, weight)
#parse_blast.pl <file>
#tab separated file BLAST 12 column output


my ($file1) = @ARGV;
open my $fh1, '<', $file1;

my $score = 0;
while (my $line = <$fh1>) {
	my @row = split(/\t/, $line);
	
	if($row[0] == $row[1]){
	
	#ignoring self matching hits
	
	}else{

	my $weight = 100;
	
	#if(0 then skipping)
	if($row[10] != 0 || $row[10] != 0.0){
		$weight = min(100, log10($row[10]));
	}
    	print"$row[0]\t$row[1]\t$weight\n";	
	}
	
}
close $fh1;

#log subroutine 
sub log10 {
        my $n = shift;
        return -1 * log($n)/log(10);
}
