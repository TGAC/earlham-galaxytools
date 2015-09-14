#!/usr/bin/perl
#
use strict;
use warnings;

use Bio::JSON;
#A simple perl parser to convert hcluster_sg 3-column output into list of ids in separate files
#hcluster_sg_parser.pl <file>
#

my $out=[];

my $tree = $ARGV[0];
my $CIGAR = $ARGV[2];
my $genes = $ARGV[1];

my $tree_string = "";
my $cigar_string = "";
my %hash;
open my $fh1, '<', $tree or die "Can't open '$tree': $!";

#reads through file
while (my $line = <$fh1>) {
    chomp($line);

   $tree_string .= $line;
}
close $fh1;



$hash{'tree'} = $tree_string;

#print $json_text;
open my $fh2, '<', $CIGAR or die "Can't open '$CIGAR': $!";;

my %cigar_hash;

#reads through file
while (my $line = <$fh2>) {
    chomp($line);
    my @row = split(/\t/, $line);
    $cigar_hash{$row[0]} = $row[1];
}
close $fh1;




$hash{'cigar'} = \%cigar_hash;

open my $fh3, '<', $genes or die "Can't open '$genes': $!";;

my $genes_string = "";
#reads through file
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