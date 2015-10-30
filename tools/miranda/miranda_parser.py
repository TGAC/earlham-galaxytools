import sys

# get hits from miranda scans
with open(sys.argv[1]) as infile1:
    with open(sys.argv[2], "w") as outfile:
        for line1 in infile1:
            if "%" in line1 and "Forward:" not in line1:
                outfile.write(line1)
