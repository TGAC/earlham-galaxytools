import argparse
import sys
import math


def main():
	parser = argparse.ArgumentParser()

	parser.add_argument('-i', metavar='in-file', type=argparse.FileType('rt'), required=True,  help='Path to input file')

	parser.add_argument('-o', metavar='out-file', type=argparse.FileType('wt'), required=True, help='Path to output file')

	parser.add_argument('-r', action='store_true', default=False,
	                    dest='reciprocal',
	                    help='Annotate homolog pair')


	parser.add_argument('--version', action='version', version='%(prog)s 1.0')

	options = parser.parse_args()
	
	result = {}
	
	for line in options.i:
		line = line.rstrip()
		
		line_cols = line.split('\t')

		if line_cols[0] != line_cols[1]:
			weight = 100

			if line_cols[10] != "0" and line_cols[10] != "0.0":
				weight = min(100, -1 * round(math.log10(float(line_cols[10]))/2))

			if line_cols[0] in result:
				if line_cols[1] not in result[line_cols[0]]:
					result[line_cols[0]].update({line_cols[1] : weight})
			else:
				result[line_cols[0]] = { line_cols[1] : weight }

			if(options.reciprocal == False):
				options.o.write("%s\t%s\t%d\n" % (line_cols[0], line_cols[1], weight))

	if(options.reciprocal):
		for i in result:
			pairs = result[i] 
			for pair in pairs:
				if pair in result:
					if i in result[pair]:
						options.o.write("%s\t%s\t%d\n" % (i, pair, pairs[pair]))

if __name__ == "__main__":
	main()
