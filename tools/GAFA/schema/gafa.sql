CREATE TABLE meta (
        version VARCHAR PRIMARY KEY NOT NULL);
CREATE TABLE gene (
        gene_id VARCHAR PRIMARY KEY NOT NULL,
        gene_symbol VARCHAR,
        species VARCHAR NOT NULL,
        gene_json VARCHAR NOT NULL);
CREATE INDEX gene_symbol_index ON gene (gene_symbol);
CREATE TABLE transcript (
        transcript_id VARCHAR PRIMARY KEY NOT NULL,
        protein_id VARCHAR UNIQUE,
        protein_sequence VARCHAR,
        gene_id VARCHAR NOT NULL REFERENCES gene(gene_id));
CREATE VIEW transcript_species as
        SELECT transcript_id, species 
        FROM transcript JOIN gene
        ON transcript.gene_id = gene.gene_id;
CREATE TABLE gene_family (
        gene_family_id INTEGER PRIMARY KEY,
        gene_tree VARCHAR NOT NULL);
CREATE TABLE gene_family_member (
        gene_family_id INTEGER NOT NULL REFERENCES gene_family(gene_family_id),
        protein_id VARCHAR KEY NOT NULL REFERENCES transcript(protein_id),
        protein_alignment VARCHAR NOT NULL,
        PRIMARY KEY (gene_family_id, protein_id));
