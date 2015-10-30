import sys

# get hits from miranda scans
cap = ""
with open (sys.argv[1]) as infile1:
    for line1 in infile1:
        line1 = line1.strip()
        if "%" in line1 and "Forward:" not in line1:
            #print(line1)
            cap = cap + line1 + "\n"
allregnettf = open(sys.argv[2], "w")
allregnettf.write(cap)
allregnettf.close()
