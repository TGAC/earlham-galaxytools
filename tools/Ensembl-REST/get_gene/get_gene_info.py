import requests
import sys
import json
import optparse

#
# A simple script to connect to Ensembl server and retrieve gene information using Ensembl REST API
# get_gene_info.py -e [0|1] -u [0|1] -f [full|condensec] -i <file-with-list-of-ids>
#

server = "http://rest.ensembl.org"
ext = "/lookup/id"

parser = optparse.OptionParser()
parser.add_option('-i', '--input', 
                  dest="input_filename", 
                  default="default.in",
                  )

parser.add_option('-f', '--format', 
                  dest="format", 
                  default="full",
                  )


parser.add_option('-e', '--expand', 
                  dest="expand", 
                  default="0",
                  )

parser.add_option('-u', '--utr', 
                  dest="utr", 
                  default="0",
                  )

options, remainder = parser.parse_args()

f = open(options.input_filename)

ids = []

for line in f:
	ids.append(line.strip()),

headers = {"Content-Type" : "application/json", "Accept" : "application/json"}

params = "?format=" + options.format + ";expand=" + options.expand + ";utr=" + options.utr

list = '{ "ids" : ["' + '", "'.join(ids) + '"]}'

r = requests.post(server + ext + params, headers=headers, data=list)

if not r.ok:
	r.raise_for_status()
	sys.exit()

decoded = r.json()


var = json.dumps(decoded)

print var