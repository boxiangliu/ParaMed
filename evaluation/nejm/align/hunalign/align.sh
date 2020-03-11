hunalign=/mnt/home/boxiang/software/hunalign-1.1/src/hunalign/hunalign
ladder2text=/mnt/home/boxiang/software/hunalign-1.1/scripts/ladder2text.py
dictionary=/mnt/home/boxiang/software/hunalign-1.1/data/null.dic
in_dir=../processed_data/evaluation/nejm/align/hunalign/input/
out_dir=../processed_data/evaluation/nejm/align/hunalign/align/
mkdir -p $out_dir


$hunalign -utf -realign -batch $dictionary $in_dir/batch

while read line; do
	src=$(echo "$line" | cut -f1)
	tgt=$(echo "$line" | cut -f2)
	ladder=$(echo "$line" | cut -f3)

	echo Source: $src
	echo Target: $tgt
	echo Alignment: $ladder

	bitext=${ladder/.ladder/.bitext}
	bitext=${bitext/$in_dir/$out_dir}
	python2.7 $ladder2text $ladder $src.mark $tgt.mark > $bitext

done < $in_dir/batch

max=$(cat $out_dir/*bitext | cut -f 1 | sort -n | tail -n1)
min=$(cat $out_dir/*bitext | cut -f 1 | sort -n | head -n1)
for i in `seq $min 0.05 $max`; do
	echo $i
	mkdir -p $out_dir/$i
	cat $out_dir/*bitext | awk '{if ($1 >= threshold) {print $0}}' threshold=$i | cut -f 2 > $out_dir/$i/align.zh
	cat $out_dir/*bitext | awk '{if ($1 >= threshold) {print $0}}' threshold=$i | cut -f 3 > $out_dir/$i/align.en
done