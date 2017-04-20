use strict;
use warnings;

my $filename = $ARGV[0]; # File containg list of UniProt identifiers.
my $format = $ARGV[1]; # Format gene, transcript, protein.

my @output;

open(my $fh, '<:encoding(UTF-8)', $filename)
  or die "Could not open file '$filename' $!";
 
while (my $row = <$fh>) {
  chomp $row;
  if ($row =~ /^(DR).*/){
    my @cols = split /\s+/, $row;
    if ($cols[1]=~ m/Ensembl/){
      if($format eq "transcript"){
        chop($cols[2]);
        push @output,$cols[2];
      } elsif($format eq "protein") {
        chop($cols[3]);
        push @output,$cols[3];
      }elsif($format eq "gene") {
        chop($cols[4]);
        push @output,$cols[4];
      }
    }
  }
}

foreach my $id (@output)
{
    print "$id\n" ;
}
