#!/bin/bash

sample_data=(`cat $1 | cut -f1 | sed ':a;N;$!ba;s/\n/ /g'`)
sample_name=(`cat $1 | cut -f2 | sed ':a;N;$!ba;s/\n/ /g'`)
sample_group=(`cat $1 | cut -f3 | sed ':a;N;$!ba;s/\n/ /g'`)


group=('#')
sample=('#Feature')

touch anno.tmp
touch count.tmp

nsamples=`expr ${#sample_data[@]} - 1`

for i in `seq 0 1 $nsamples`; do
	group+=(${sample_group[i]}:${sample_group[i]})
	sample+=(${sample_name[i]})

	cat ${sample_data[i]} | tail -n+3 > dataWithoutHeader

	cat dataWithoutHeader | sort -k1 > dataWithoutHeader.sorted 

	cat dataWithoutHeader.sorted | awk '{print $1}' > anno.sample 
	cat dataWithoutHeader.sorted | awk '{print $5}' > count.sample 

	paste -d"\t" count.tmp count.sample > count 
	paste -d"\t" anno.tmp anno.sample > anno 

	cat count > count.tmp
	cat anno > anno.tmp

done

echo ${group[*]} | sed -e 's/ /\t/g' > count.matrix
echo ${sample[*]} | sed -e 's/ /\t/g' >> count.matrix

cat count | cut -f 2- > count.tmp

paste -d"\t" anno.sample count.tmp >> count.matrix

cat anno.tmp | cut -f 2- | awk '{for (i=2; i<=NF; i++){if ($1!=$i){print "error"; break}}}' > control.data

echo -e "gene_ID\tstart_coord\tend_coord" > annotation
cat dataWithoutHeader.sorted | awk '{print $1"\t"$2"\t"$3}' >> annotation

if [[ -s control.data ]]; then
	echo "" > count.matrix
	echo "" > annotation
	echo ERROR: gene_ID\'s have to be in the same order in each sample_data file.
	exit 1
else
	echo "Done."
fi
