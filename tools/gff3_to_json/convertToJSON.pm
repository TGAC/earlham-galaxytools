#!/usr/bin/env perl
#
#    Read GFF file and write as JSON (JSON Gene Format)
#
#    AUTHOR:Anil Thanki (Anil.Thanki@tgac.ac.uk || thanki.anil@gmail.com)
#
#

package gff2JSON;
use strict;


use JSON;

sub genetoJSON(){

    my %gene;
    my @data = @_;

    my @note = split(";",$data[8]);
    $gene{'Transcript'} = [];

    $gene{'start'} = int($data[3]);
    $gene{'end'} = int($data[4]);
    $gene{'seq_region_name'} = $data[0];


    if($data[6] eq '+'){
        $gene{'strand'} = 1;
    }else{
        $gene{'strand'} = -1;
    }
    
    foreach my $attr(@note){
        my @node = split("=",$attr);

        if($node[0] eq 'ID'){
            $gene{'id'} = $node[1];
        }else{
            $gene{$node[0]} = $node[1];
        }
    }

    $gene{'species'} = $data[-1];
    $gene{'member_id'} = $gff2JSON::gene_id;
    $gff2JSON::gene_id++;
    $gff2JSON::gene_hash{$gene{'id'}} = \%gene;

}

sub mrnatoJSON(){

    my %mrna;
    my @data = @_;
    my @note = split(";",$data[8]);
    $mrna{'Exon'} = [];
    $mrna{'CDS'} = [];
    # $gene{'Translation'} = {};
    # $mrna{'translation_start'} = 0;
    # $mrna{'translation_end'} = 0;
    $mrna{'start'} = int($data[3]);
    $mrna{'end'} = int($data[4]);
    $mrna{'seq_region_name'} = $data[0];

    if($data[6] eq '+'){
        $mrna{'strand'} = 1;
    }else{
        $mrna{'strand'} = -1;
    }
    
    foreach my $attr(@note){
        my @node = split("=",$attr);

        if($node[0] eq "ID"){
            $mrna{'id'} = $node[1];
        }else{
            $mrna{$node[0]} = $node[1];
        }
    }

    $gff2JSON::mRNA_hash{$mrna{'id'}} = \%mrna;
}

sub exontoJSON(){
    my %exon;
    my @data = @_;
    my @note = split(";",$data[8]);

    $exon{'start'} = int($data[3]);
    $exon{'end'} = int($data[4]);
    $exon{'length'} = $data[4] - $data[3] + 1;


    if($data[6] eq '+'){
        $exon{'strand'} = 1;
    }else{
        $exon{'strand'} = -1;
    }
    
    foreach my $attr(@note){
        my @node = split("=",$attr);

        if($node[0] eq "ID"){
            $exon{'id'} = $node[1];
        }else{
            $exon{$node[0]} = $node[1];
        }
    }
    if($exon{'ID'} or $exon{'id'}){

    }else{
        $exon{'id'} = $exon{'Parent'}.int(rand(100))
    }
    if($exon{'Parent'}){
        if(exists $gff2JSON::exon_hash{$exon{'Parent'}}){
            push $gff2JSON::exon_hash{$exon{'Parent'}}, \%exon;
        }else{
            $gff2JSON::exon_hash{$exon{'Parent'}} = [];
            push $gff2JSON::exon_hash{$exon{'Parent'}}, \%exon;
        }
    }

}

sub cdstoJSON(){
    my %cds;
    my @data = @_;
    my @note = split(";",$data[8]);

    $cds{'start'} = int($data[3]);
    $cds{'end'} = int($data[4]);

    if($data[6] eq '+'){
        $cds{'strand'} = 1;
    }else{
        $cds{'strand'} = -1;
    }
    
    foreach my $attr(@note){
        my @node = split("=",$attr);
        $cds{$node[0]} = $node[1];
    }
    if($cds{'id'}){

        }else{
            $cds{'id'} = $cds{'Parent'}.int(rand(100))
        }

    if($cds{'Parent'}){
        if(exists $gff2JSON::cds_hash{$cds{'Parent'}}){
            push $gff2JSON::cds_hash{$cds{'Parent'}}, \%cds;
        }else{
            $gff2JSON::cds_hash{$cds{'Parent'}} = [];
            push $gff2JSON::cds_hash{$cds{'Parent'}}, \%cds;
        }
    }

}

sub fiveutrtoJSON(){

    my %utr;
    my @data = @_;
    my @note = split(";",$data[8]);

    $utr{'start'} = $data[3];
  
    $gff2JSON::fiveutr_hash{$utr{'Parent'}} = $utr{'start'};

}

sub threeutrtoJSON(){

    my %utr;
    my @data = @_;
    my @note = split(";",$data[8]);

    $utr{'end'} = $data[4];

    $gff2JSON::threeutr_hash{$utr{'Parent'}} = $utr{'end'} ;

}

sub joinJSON(){

    foreach my $key (keys %gff2JSON::exon_hash) {

        my @data = @{ $gff2JSON::exon_hash{$key} };

        my @sorted =  sort { $a->{start} <=> $b->{start} } @data;

        $gff2JSON::exon_hash{$key} = [];

        push $gff2JSON::exon_hash{$key}, @sorted;


        if($gff2JSON::mRNA_hash{$key}){
            $gff2JSON::mRNA_hash{$key}{'Exon'} = $gff2JSON::exon_hash{$key};
        }
    }

    foreach my $key (keys %gff2JSON::cds_hash) {

        my @data = @{ $gff2JSON::cds_hash{$key} };

        my @sorted =  sort { $a->{start} <=> $b->{start} } @data;

        $gff2JSON::cds_hash{$key} = [];
        
        push $gff2JSON::cds_hash{$key}, @sorted;

        if($gff2JSON::mRNA_hash{$key}){
            $gff2JSON::mRNA_hash{$key}{'CDS'} =  $gff2JSON::cds_hash{$key};
        }
    }

    foreach my $key (keys %gff2JSON::threeutr_hash) {
        if($gff2JSON::mRNA_hash{$key}){
            $gff2JSON::mRNA_hash{$key}{'Translation'}{'start'} =  int($gff2JSON::threeutr_hash{$key});
        }
    }

    foreach my $key (keys %gff2JSON::fiveutr_hash) {
        if($gff2JSON::mRNA_hash{$key}){
            $gff2JSON::mRNA_hash{$key}{'Translation'}{'end'} = int($gff2JSON::fiveutr_hash{$key});
        }
    }

      for my $key ( keys %gff2JSON::cds_hash ) {
        if(int($gff2JSON::mRNA_hash{$key}{'Translation'}{'start'}) == 0 && int($gff2JSON::mRNA_hash{$key}{'Translation'}{'end'}) == 0 ){
        my @temp_cds  =  @{ $gff2JSON::cds_hash{$key} };
        my @temp_exon  =  @{ $gff2JSON::exon_hash{$key} };
        

        my $exon_start =0;
        my $exon_end =0;
        my $cds_start =0;

        my $cds_end = 0;
        my $j = 0;    
        for my $i ( 0 .. $#temp_exon ) {
            for my $role ( keys %{ $temp_exon[$i] } ) {
                if($role eq "start"){
                    $exon_start = $temp_exon[$i]{$role} ;
                    $cds_start = $temp_cds[$j]{$role} ;
                }
                if($role eq "end"){
                    $exon_end = $temp_exon[$i]{$role} ;
                    $cds_end = $temp_cds[$j]{$role} ;
                }
            }
            if( int($exon_start) >= int($cds_start))
            {
                $j++;
                 if(int($cds_start) > 0){
                    if(int($gff2JSON::mRNA_hash{$key}{'Translation'}{'start'}) == 0 ){
                        $gff2JSON::mRNA_hash{$key}{'Translation'}{'start'} = int($cds_start);
                    }
                    $gff2JSON::mRNA_hash{$key}{'Translation'}{'end'} = int($cds_end);
                }
            } 
        }
        }
        
    }

    foreach my $key (keys %gff2JSON::mRNA_hash) {
        my $parent = $gff2JSON::mRNA_hash{$key}{'Parent'};
        if($gff2JSON::gene_hash{$parent}){
            push $gff2JSON::gene_hash{$parent}{'Transcript'}, $gff2JSON::mRNA_hash{$key};
            my $species = $gff2JSON::gene_hash{$parent}{'species'};
            $gff2JSON::gene_hash{$parent} = $gff2JSON::gene_hash{$parent};

        }
    }

    print JSON->new->pretty->encode(\%gff2JSON::gene_hash);

}
1;
