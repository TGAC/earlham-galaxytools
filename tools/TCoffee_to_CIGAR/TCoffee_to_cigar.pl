#!/usr/bin/perl
#
use strict;
use warnings;

#A simple perl parser to convert 2-column output where first column is fasta id and second is alignment sequence into 2-column output where first column is fasta id and second is CIGAR line
#TCoffee_to_cigar.pl <file>

my $file1 = $ARGV[0];
open my $fh1, '<', $file1;

#reads through file
while (my $line = <$fh1>) {
    chomp $line;
    my @row = split(/\t/, $line);

    # Converts each match into M and each gap into D
    my $long_cigar = $row[1];
    $long_cigar =~ s/[^-]/M/g;
    $long_cigar =~ s/-/D/g;

    # Split the $long_cigar in substrings composed by the same letter
    $long_cigar =~ s/DM/D,M/g;
    $long_cigar =~ s/MD/M,D/g;
    my @cigar_array = split(',', $long_cigar);

    # Condense each substring, e.g. DDDD in 4D, and concatenate them again
    my $cigar = '';
    foreach my $str (@cigar_array) {
        if (length($str) > 1) {
            $cigar .= length($str);
        }
        $cigar .= substr($str, 0, 1);
    }
    print "$row[0]\t$cigar\n";
}
close $fh1;
