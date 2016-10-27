#!/usr/bin/perl
#
use strict;
use warnings;

# A simple Perl script to convert FASTA sequence alignments into 2-column output where first column is FASTA id and second is CIGAR line
# TCoffee_to_cigar.pl <file>

sub convert_and_print {
    my ($header, $sequence) = @_;
    # Converts each match into M and each gap into D
    $sequence =~ s/[^-]/M/g;
    $sequence =~ s/-/D/g;

    # Split the sequence in substrings composed by the same letter
    $sequence =~ s/DM/D,M/g;
    $sequence =~ s/MD/M,D/g;
    my @cigar_array = split(',', $sequence);

    # Condense each substring, e.g. DDDD in 4D, and concatenate them again
    my $cigar = '';
    foreach my $str (@cigar_array) {
        if (length($str) > 1) {
            $cigar .= length($str);
        }
        $cigar .= substr($str, 0, 1);
    }
    print "$header\t$cigar\n";
}

my $file1 = $ARGV[0];
open my $fh1, '<', $file1;

my $header = '', my $sequence = '';
while (my $line = <$fh1>) {
    chomp $line;
    if (substr($line, 0, 1) eq '>') {
        if ($header) {
            convert_and_print($header, $sequence);
        }
        $header = substr($line, 1);
        $sequence = '';
    } else {
        $sequence .= $line;
    }
}
close $fh1;
convert_and_print($header, $sequence);
