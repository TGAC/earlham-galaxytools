#!/usr/bin/python

import requests
import sys
import optparse
import json
 
#
# A simple parser to connect to Ensembl server and retrieve gene information using Ensembl REST aPI
# get_gene_info.py --expand_3prime [number] --expand_5prime [number] -t [genomic|cds|cdna|protein] -m [1|0] -i <file-with-list-of-ids>
#


server = "http://rest.ensembl.org"
ext = "/sequence/id"

parser = optparse.OptionParser()
parser.add_option('-i', '--input', 
                  dest="input_filename", 
                  default="default.in",
                  )

parser.add_option('-t', '--type', 
                  dest="type", 
                  default="genomic",
                  )


parser.add_option('--expand_3prime', 
                  dest="expand_3prime", 
                  default="0",
                  )

parser.add_option('--expand_5prime', 
                  dest="expand_5prime", 
                  default="0",
                  )

parser.add_option('-m', '--multiple_sequences', 
                  dest="multiple_sequences", 
                  default="0",
                  )

options, remainder = parser.parse_args()

f = open(options.input_filename)

ids = []

for line in f:
	ids.append(line.strip()),

headers={ "Content-Type" : "application/json", "Accept" : "application/json"}

params = "?type="+ options.type + ";expand_3prime=" + options.expand_3prime + ";expand_5prime=" + options.expand_5prime +  ";multiple_sequences=" + options.multiple_sequences

list = '{ "ids" : ["' + '", "'.join(ids) + '"]}'

r = requests.post(server + ext + params, headers=headers, data=list)
 
if not r.ok:
  r.raise_for_status()
  sys.exit()


decoded = r.json()

var = json.dumps(decoded)

print var