#!/usr/bin/perl
use strict;
use warnings;
use List::Util qw(min max);

# A simple Perl parser to convert a BLAST 12-column or 24-column output into a
# 3-column input for hcluster_hg (id1, id2, weight):
# parse_blast.pl <file>

use constant LOG_E_10 => log(10);

my $file1 = $ARGV[0];
open my $fh1, '<', $file1;

while (my $line = <$fh1>) {
    my @row = split(/\t/, $line);

    if ($row[0] eq $row[1]) {
        # ignore self matching hits
    } else {
        # Convert evalue to an integer weight with max 100
        my $weight = 100;

        #if the evalue is 0, leave weight at 100
        if ($row[10] != 0 && $row[10] != 0.0) {
            $weight = min(100, positive_round(-1 * log10($row[10])));
        }
        print"$row[0]\t$row[1]\t$weight\n";
    }
}
close $fh1;

# Calculate logarithm to base 10 of a number
sub log10 {
    my $n = shift;
    return log($n) / LOG_E_10;
}

# Round a positive float to the nearest integer
sub positive_round{
    my $n = shift;
    return int($n + 0.5);
}
