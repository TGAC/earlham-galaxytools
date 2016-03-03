#!/usr/bin/perl
#
use strict;
use warnings;
# A simple perl parser to convert hcluster_sg 3-column output into list of ids in separate files
# hcluster_sg_parser.pl <file>

my $file1 = $ARGV[0];
open my $fh1, '<', $file1;

while (my $line = <$fh1>) {
    chomp $line;
    my @row = split(/\t/, $line);

    my $cluster_id = $row[0];
    my $id_list = $row[2];
    # Change commas to newlines
    $id_list =~ s/\,/\n/g;

    my $outfile = $cluster_id."_output.txt";
    open(my $fh, '>', $outfile) or die "Could not open file '$outfile' for writing: $!";
    print $fh $id_list;
    close $fh;
}
close $fh1;
