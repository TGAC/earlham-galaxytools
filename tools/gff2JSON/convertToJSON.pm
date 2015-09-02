#!/usr/bin/env perl
#
#    Read GFF file and write as JSON (JSON Gene Format)
#
#    AUTHOR:Anil Thanki (Anil.Thanki@tgac.ac.uk || thanki.anil@gmail.com)
#
#

package gff2JSON;
use strict;
use warnings;


use Bio::JSON;

sub genetoJSON(){

    my %gene;
    my @data = @_;

    my @note = split(";",$data[8]);
    $gene{'Transcript'} = [];

    $gene{'start'} = $data[3];
    $gene{'end'} = $data[4];
    $gene{'referece'} = $data[0];


    if($data[6] eq '+'){
        $gene{'strand'} = 1;
    }else{
        $gene{'strand'} = -1;
    }
    
    foreach my $attr(@note){
        my @node = split("=",$attr);
        $gene{$node[0]} = $node[1];
    }

    $gene{'genome'} = $gff2JSON::genome;
    $gene{'member_id'} = $gff2JSON::gene_id;

    $gff2JSON::gene_id++;
    $gff2JSON::gene_hash{$gene{'ID'}} = \%gene;


}

sub mrnatoJSON(){

    my %mrna;
    my @data = @_;
    my @note = split(";",$data[8]);
    $mrna{'Exon'} = [];
    $mrna{'3UTR'} = [];
    $mrna{'5UTR'} = [];
    $mrna{'start'} = $data[3];
    $mrna{'end'} = $data[4];
    $mrna{'referece'} = $data[0];

    if($data[6] eq '+'){
        $mrna{'strand'} = 1;
    }else{
        $mrna{'strand'} = -1;
    }
    
    foreach my $attr(@note){
        my @node = split("=",$attr);
        $mrna{$node[0]} = $node[1];
    }

    $gff2JSON::mRNA_hash{$mrna{'ID'}} = \%mrna;
}

sub exontoJSON(){
    my %exon;
    my @data = @_;
    my @note = split(";",$data[8]);

    $exon{'start'} = $data[3];
    $exon{'end'} = $data[4];

    if($data[6] eq '+'){
        $exon{'strand'} = 1;
    }else{
        $exon{'strand'} = -1;
    }
    
    foreach my $attr(@note){
        my @node = split("=",$attr);
        $exon{$node[0]} = $node[1];
    }
    if($exon{'ID'}){

        }else{
            $exon{'ID'} = $exon{'Parent'}.int(rand(100))
        }

    $gff2JSON::exon_hash{$exon{'ID'}} = \%exon;

}

sub fiveutrtoJSON(){

    my %utr;
    my @data = @_;
    my @note = split(";",$data[8]);

    $utr{'start'} = $data[3];
    $utr{'end'} = $data[4];

    if($data[6] eq '+'){
        $utr{'strand'} = 1;
    }else{
        $utr{'strand'} = -1;
    }
    
    foreach my $attr(@note){
        my @node = split("=",$attr);
        $utr{$node[0]} = $node[1];
    }

    $gff2JSON::fiveutr_hash{$utr{'ID'}} = \%utr;

}

sub threeutrtoJSON(){

    my %utr;
    my @data = @_;
    my @note = split(";",$data[8]);

    $utr{'start'} = $data[3];
    $utr{'end'} = $data[4];

    if($data[6] eq '+'){
        $utr{'strand'} = 1;
    }else{
        $utr{'strand'} = -1;
    }
    
    foreach my $attr(@note){
        my @node = split("=",$attr);
        $utr{$node[0]} = $node[1];
    }

    $gff2JSON::threeutr_hash{$utr{'ID'}} = \%utr;

}

sub joinJSON(){
    foreach my $key (keys %gff2JSON::exon_hash) {
        my $parent = $gff2JSON::exon_hash{$key}{'Parent'};
        if($gff2JSON::mRNA_hash{$parent}){
            push $gff2JSON::mRNA_hash{$parent}{'Exon'}, $gff2JSON::exon_hash{$key};
        }
    }

    foreach my $key (keys %gff2JSON::threeutr_hash) {
        my $parent = $gff2JSON::threeutr_hash{$key}{'Parent'};
        if($gff2JSON::mRNA_hash{$parent}){
            push $gff2JSON::mRNA_hash{$parent}{'3UTR'}, $gff2JSON::threeutr_hash{$key};
        }
    }

    foreach my $key (keys %gff2JSON::fiveutr_hash) {
        my $parent = $gff2JSON::fiveutr_hash{$key}{'Parent'};
        if($gff2JSON::mRNA_hash{$parent}){
            push $gff2JSON::mRNA_hash{$parent}{'5UTR'}, $gff2JSON::fiveutr_hash{$key};
        }
    }

    foreach my $key (keys %gff2JSON::mRNA_hash) {
        my $parent = $gff2JSON::mRNA_hash{$key}{'Parent'};
        if($gff2JSON::gene_hash{$parent}){
            push $gff2JSON::gene_hash{$parent}{'Transcript'}, $gff2JSON::mRNA_hash{$key};
        }
    }
    print JSON->new->pretty->encode(\%gff2JSON::gene_hash);
}
1;
