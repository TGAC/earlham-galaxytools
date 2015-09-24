#!/usr/bin/perl
#
use strict;
use warnings;

use JSON;
#A simple perl script to generate Aequatus from Newick from TreeBest best, Gene JSON file and CIGAR table format output of TCoffee-to-CIGAR
#aequatus-generator.pl <tree-file> <Gene JSON file> <CIGAR file> 
#

my $tree = $ARGV[0];
my $genes = $ARGV[1];
my $CIGAR = $ARGV[2];

my $tree_string = "";
my $cigar_string = "";
my %hash;
open my $fh1, '<', $tree or die "Can't open '$tree': $!";

#reads through Tree file
while (my $line = <$fh1>) {
    chomp($line);

   $tree_string .= $line;
}
close $fh1;

$hash{'tree'} = $tree_string;

open my $fh2, '<', $CIGAR or die "Can't open '$CIGAR': $!";;

my %cigar_hash;

#reads through CIGAR file
while (my $line = <$fh2>) {
    chomp($line);
    my @row = split(/\t/, $line);
    $cigar_hash{$row[0]} = $row[1];
}
close $fh1;

$hash{'cigar'} = \%cigar_hash;

open my $fh3, '<', $genes or die "Can't open '$genes': $!";;

my $genes_string = "";

#reads through Gene file
while (my $line = <$fh3>) {
    chomp($line);
    $line =~ s/\s//g;
    $genes_string .= $line;
}
close $fh1;

my $json = JSON->new->allow_nonref;

my $json_text = $json->decode($genes_string);

$hash{'member'} = $json_text;

print JSON->new->encode(\%hash);