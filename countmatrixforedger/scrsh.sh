#!/bin/bash

#sample_data=(tmp tmp1 tmp2 tmp3)
sample_data=(`cat $1 | cut -f1 | sed ':a;N;$!ba;s/\n/ /g'`)
#sample_name=(sample1 sample2 sample3 sample4)
sample_name=(`cat $1 | cut -f2 | sed ':a;N;$!ba;s/\n/ /g'`)
#sample_group=(gr1 gr1 gr2 gr2)
sample_group=(`cat $1 | cut -f3 | sed ':a;N;$!ba;s/\n/ /g'`)


group=('#')
sample=('#Feature')

touch anno.tmp
touch count.tmp

nsamples=`expr ${#sample_data[@]} - 1`

for i in `seq 0 1 $nsamples`; do
	group+=(${sample_group[i]}:${sample_group[i]})
	sample+=(${sample_name[i]})

	cat ${sample_data[i]} | tail -n+3 > dataWithoutHeader 2>> script.log

	cat dataWithoutHeader | sort -k1 > dataWithoutHeader.sorted 2>> script.log

	cat dataWithoutHeader.sorted | awk '{print $1}' > anno.sample 2>> script.log
	cat dataWithoutHeader.sorted | awk '{print $5}' > count.sample 2>> script.log

	paste -d"\t" count.tmp count.sample > count 2>> script.log
	paste -d"\t" anno.tmp anno.sample > anno 2>> script.log

	cat count > count.tmp 2>> script.log
	cat anno > anno.tmp 2>> script.log

done

echo ${group[*]} | sed -e 's/ /\t/g' > count.matrix 2>> script.log
echo ${sample[*]} | sed -e 's/ /\t/g' >> count.matrix 2>> script.log

cat count | cut -f 2- > count.tmp 2>> script.log

paste -d"\t" anno.sample count.tmp >> count.matrix 2>> script.log

cat anno.tmp | cut -f 2- | awk '{for (i=2; i<=NF; i++){if ($1!=$i){print "error"; break}}}' > control.data 2>> script.log

echo -e "gene_ID\tstart_coord\tend_coord" > annotation 2>> script.log
cat dataWithoutHeader.sorted | awk '{print $1"\t"$2"\t"$3}' >> annotation 2>> script.log

if [[ -s control.data ]]; then
	echo "kolumny nie sa w odpowiedniej kolejnosci" > error.log
	echo "" > count.matrix
	echo "" > annotation
else
	echo "" > error.log
fi
