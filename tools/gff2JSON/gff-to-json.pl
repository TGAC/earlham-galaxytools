#!/usr/bin/env perl
#
#	Read GFF file and write as JSON (JSON Gene Format)
#
#   AUTHOR:Gemy George Kaithakottil (gemy.kaithakottil@tgac.ac.uk || gemygk@gmail.com)
#
#

package gff2JSON;
use strict;
use warnings;

use Bio::JSON;
use convertToJSON;

my $usage = "
	Read GFF file

	Usage: perl $0 <file.gff>

	OUTPUT to STDOUT

	\n";

my $transcripts = shift or die $usage;

my $gene_id=0;
my $mrna_id=0;

	our %gene_hash;
	our %mRNA_hash;
	our %exon_hash;
	our %threeutr_hash;
	our %fiveutr_hash;

# GFF3 file
open(FILE,$transcripts) or die "$!";
while (<FILE>) { # Read lines from file(s) specified on command line. Store in $_.
    s/#.*//; # Remove comments from $_.
    next unless /\S/; # \S matches non-whitespace.  If not found in $_, skip to next line.
	chomp;
	my @f = split (/\t/); # split $_ at tabs separating fields.

	if($f[2] eq "gene") {
		# Gene ID
		$f[8] =~ /ID\s*=\s*([^;]+)/;
		$gene_id = $1;
		$gene_id =~ s/\s+$//;

		# Gene Note
		my $gene_note=undef;
		if( $f[8] =~ /Note\s*=\s*([^;]+)/ ) {
			#$f[8] =~ /Note\s*=\s*([^;]+)/;
			$gene_note = $1;
			$gene_note =~ s/\s+$//;
		}
		# Gene biotype:
		my $gene_biotype=undef;
		if ( $f[8] =~ /biotype\s*=\s*([^;]+)/ ) {
			$gene_biotype = $1;
			$gene_biotype =~ s/\s+$//;
		}
		&genetoJSON(@f);

		
	}
	elsif($f[2] eq "mRNA" || $f[2] eq "transcript") {
		# mRNA ID
		$f[8] =~ /ID\s*=\s*([^;]+)/;
		$mrna_id = $1;
		$mrna_id =~ s/\s+$//;
		# mRNA parent
		$f[8] =~ /Parent\s*=\s*([^;]+)/;
		my $parent_id = $1;
		$parent_id =~ s/\s+$//;
		# mRNA Note
		my $mrna_note=undef;
		if( $f[8] =~ /Note\s*=\s*([^;]+)/ ) {
			#$f[8] =~ /Note\s*=\s*([^;]+)/;
			$mrna_note = $1;
			$mrna_note =~ s/\s+$//;
		}
		# mRNA Name
		my $mrna_name=undef;
		if( $f[8] =~ /Name\s*=\s*([^;]+)/ ) {
			$mrna_name = $1;
			$mrna_name =~ s/\s+$//;
		}
		my $mrna_biotype=undef;
		if ( $f[8] =~ /biotype\s*=\s*([^;]+)/ ) {
			$mrna_biotype = $1;
			$mrna_biotype =~ s/\s+$//;
		}
		&mrnatoJSON(@f);
	
	}
	elsif($f[2] eq "exon") {
		# exon ID
		my $exon_id=undef;
		if ( $f[8] =~ /ID\s*=\s*([^;]+)/ ) {
			$exon_id = $1;
			$exon_id =~ s/\s+$//;
		}
		# exon parent
		$f[8] =~ /Parent\s*=\s*([^;]+)/;
		my $parent_id = $1;
		$parent_id =~ s/\s+$//;

		
		&exontoJSON(@f);
	
	}
#	elsif($f[2] eq "CDS") {
#		# CDS ID
#		$f[8] =~ /ID\s*=\s*([^;]+)/;
#		my $cds_id = $1;
#		$cds_id =~ s/\s+$//;
#		# CDS parent
#		$f[8] =~ /Parent\s*=\s*([^;]+)/;
#		my $parent_id = $1;
#		$parent_id =~ s/\s+$//;
#
#		print "$f[2]\t$f[0]\t$f[1]\t$f[2]\t$f[3]\t$f[4]\t$f[5]\t$f[6]\t$f[7]\tID=$cds_id;Parent=$parent_id\n";
#	}
	elsif($f[2] =~ /five_prime_UTR/i) {
		# 5'UTR ID
		$f[8] =~ /ID\s*=\s*([^;]+)/;
		my $utr5_id = $1;
		$utr5_id =~ s/\s+$//;
		# 5'UTR parent
		$f[8] =~ /Parent\s*=\s*([^;]+)/;
		my $parent_id = $1;
		$parent_id =~ s/\s+$//;
		&fiveutrtoJSON(@f);
	}
	elsif($f[2] =~ /three_prime_UTR/i) {
		# 3'UTR ID
		$f[8] =~ /ID\s*=\s*([^;]+)/;
		my $utr3_id = $1;
		$utr3_id =~ s/\s+$//;
		# 3'UTR parent
		$f[8] =~ /Parent\s*=\s*([^;]+)/;
		my $parent_id = $1;
		$parent_id =~ s/\s+$//;
		&threeutrtoJSON(@f);
	}
#	elsif ($f[2] eq "intron") {
#		# intron
#		$f[8] =~ /ID\s*=\s*([^;]+)/;
#		my $intron_id = $1;
#		$intron_id =~ s/\s+$//;
#		# intron parent
#		$f[8] =~ /Parent\s*=\s*([^;]+)/;
#		my $parent_id = $1;
#		$parent_id =~ s/\s+$//;
#
#		print "$f[2]\t$f[0]\t$f[1]\t$f[2]\t$f[3]\t$f[4]\t$f[5]\t$f[6]\t$f[7]\tID=$intron_id;Parent=$parent_id\n";
#	}
}
joinJSON();



close(FILE);

exit;
