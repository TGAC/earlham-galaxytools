import json
import optparse

cigar_dict = dict()
aequatus_dict = dict()
checker = None


def write_json(outfile=None, sort_keys=False):
	if outfile:
		with open(outfile, 'w') as f:
			json.dump(aequatus_dict, f)
	else:
		print json.dumps(aequatus_dict, indent=3, sort_keys=sort_keys)

def cigar_to_json(fname):
	with open(fname) as f:
		cigar = f.read().splitlines()

	for element in cigar:
		cigar_dict [element.split("\t")[3]] = element.split("\t")[2]


def newicktree_to_json(fname):
	with open(fname) as f:
		return f.read()
	
def jsontree_to_json(fname):
	with open(fname) as f:
		return json.load(f)['tree']

def gene_to_json(fname):
	with open(fname) as f:
		return json.load(f)


def join_json(tree_dict, gene_dict):
	aequatus_dict["tree"] = tree_dict
	aequatus_dict["member"] = gene_dict

	if checker:
		aequatus_dict["cigar"] = cigar_dict




def __main__():

	global checker

	parser = optparse.OptionParser()
	parser.add_option('-t', '--tree', help='Tree file')
	parser.add_option('-f', '--format', type='choice', choices=['newick', 'json'], default='json', help='Tree Format')
	parser.add_option('-c', '--cigar', help='Cigar file in table format')
	parser.add_option('-g', '--gene', help='Gene file')
	parser.add_option('-o', '--output', help='Path of the output file. If not specified, will print on the standard output')

	options, args = parser.parse_args()

	if args:
		raise Exception('Use options to provide inputs')

	if (options.format == "newick"):
		checker = True;
		cigar_to_json(options.cigar)
		tree_dict = newicktree_to_json(options.tree)
	else:
		tree_dict = jsontree_to_json(options.tree)

	gene_dict = gene_to_json(options.gene)

	join_json(tree_dict, gene_dict)

	write_json(options.output)

if __name__ == '__main__':
	__main__()