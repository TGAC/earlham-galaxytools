#!/usr/bin/env perl
#
#    Read GFF file and write as JSON (JSON Gene Format)
#
#    AUTHOR:Gemy George Kaithakottil (gemy.kaithakottil@tgac.ac.uk || gemygk@gmail.com)
#
#

package gff2JSON;
use strict;
use warnings;

use Bio::JSON;
use convertToJSON;
use File::Basename;

my $usage = "
    Read GFF file

    Usage: perl $0 <file.gff>

    OUTPUT to STDOUT

    \n";

my $fullspec = shift or die $usage;

my $gene_id="";
my $mrna_id="";
our %gene_hash;
our %mRNA_hash;
our %exon_hash;
our %threeutr_hash;
our %fiveutr_hash;
our %cds_hash;
# GFF3 file
open(FILE,$fullspec) or die "$!";

my($file, $dir, $ext) = fileparse($fullspec, qr/\.[^.]*/);
our $genome = $file;


while (<FILE>) { # Read lines from file(s) specified on command line. Store in $_.
    my $line = $_;
    $line =~ s/#.*//; # Remove comments from $_.
    $line =~ s/\r|\n//g; # 
    
    next unless /\S/; # \S matches non-whitespace.  If not found in $_, skip to next line.
    chomp;
    my @f = split (/\t/, $line); 

    if($f[2] eq "gene") {
        # Gene:
        &genetoJSON(@f);
    }
    elsif($f[2] eq "mRNA" || $f[2] eq "transcript") {
        # mRNA 
        &mrnatoJSON(@f);
    }
    elsif($f[2] eq "exon") {
        # exon
        &exontoJSON(@f);
    }
    elsif($f[2] =~ /five_prime_UTR/i) {
        # 5'UTR
        &fiveutrtoJSON(@f);
    }
    elsif($f[2] =~ /three_prime_UTR/i) {
        # 3'UTR
        &threeutrtoJSON(@f);
    }
    elsif($f[2] =~ /cds/i) {
        # 3'UTR
        &cdstoJSON(@f);
    }
}
joinJSON();

close(FILE);

exit;
