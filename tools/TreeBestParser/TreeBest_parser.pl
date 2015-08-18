#!/usr/bin/perl
use strict;
use warnings;

use Bio::Phylo::IO;
use Bio::JSON;


#A simple perl parser to convert TreeBest newick output into JSON formatted tree
#TreeBest_parser.pl <file>


my ($file1) = @ARGV;
open my $fh1, '<', $file1;

#Parse Newick file into Phylo Object
my $forest=Bio::Phylo::IO->parse(-file=>$file1, -format=>"newick");


#Loop through each object and convert into JSON object
while (my $tree=$forest->next) {
    my $out=[];
    my $children=$out;
    my $cur;
    my $parent;
    $tree->visit_breadth_first(
             -pre=>sub { 
                $cur={ 
                        name=>shift->get_name 
                    }; 
                    push @$children, $cur; 
            },
             -pre_daughter=>sub { 
                 $cur->{children}=[]; 
                 $parent=$cur; 
                 $children=$cur->{children} 
             },
        );
    print JSON->new->pretty->encode($out);
}