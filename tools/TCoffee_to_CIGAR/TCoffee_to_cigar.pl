#!/usr/bin/perl
#
use strict;
use warnings;
use List::Util qw(min max);


#Git Copy
#A simple perl parser to convert 2-column output where first column is fasta id and second is alignment sequence into 2-column output where first column is fasta id and second is CIGAR line
#TCoffee_to_cigar.pl <file>
#


my $file1 = $ARGV[0];
open my $fh1, '<', $file1;

#reads through file
while (my $line = <$fh1>) {
    my @row = split(/\t/, $line);
    my $cigar = "";
    my @alignment = split("",$row[1]);

    #converts gaps into D and match part into M
    for (my $i=0; $i<$#alignment; $i++){
        if($alignment[$i] eq '-'){
            $cigar.= "D";
        }else{
            $cigar.= "M";
        }
    }

    my $find = "DM";
    my $replace = "D,M";
    $cigar =~ s/$find/$replace/g;
    $find = "MD";
    $replace = "M,D";
    $cigar =~ s/'MD'/'M,D'/g;
    $cigar =~ s/$find/$replace/g;

    my @cigar_array = split(",",$cigar);

    $cigar = "";

    #converts string to CIGAR form with no of match and deletions
    for (my $i=0; $i<$#cigar_array; $i++){
        if(length($cigar_array[$i]) > 1){
            $cigar.= length($cigar_array[$i]);
        }
        $cigar.= substr( $cigar_array[$i], 0 , 1 );
    }
    print "$row[0]\t$cigar\n";    

}
close $fh1;
