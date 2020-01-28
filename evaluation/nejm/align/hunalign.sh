hunalign=/mnt/home/boxiang/software/hunalign-1.1/src/hunalign/hunalign
ladder2text=/mnt/home/boxiang/software/hunalign-1.1/scripts/ladder2text.py
dictionary=/mnt/home/boxiang/software/hunalign-1.1/data/null.dic
in_dir=../processed_data/evaluation/nejm/translation/
out_dir=../processed_data/evaluation/nejm/align/hunalign/
mkdir -p $out_dir $out_dir/input


for a in $(ls $in_dir/doc*_*.snt); do
	echo $a
	base=$(basename $a)
	out_fn=$out_dir/input/$base
	cut -d "|" -f 1 $a > $out_fn
done

[[ -f $out_dir/batch ]] && rm $out_dir/batch
for src in $(ls $out_dir/input/doc*_zh.snt); do
	tgt=${src/_zh/_en}
	out=${src/_zh.snt/.ladder}
	out=${out/input/}
	echo -e "$src\t$tgt\t$out" >> $out_dir/batch
done

$hunalign -utf -autodict=$out_dir/auto.dic $dictionary \
/mnt/scratch/boxiang/projects/med_translation/processed_data/evaluation/nejm/translation/tmp/wmt18_zh.snt \
/mnt/scratch/boxiang/projects/med_translation/processed_data/evaluation/nejm/translation/tmp/wmt18_en.snt

head -n40000 /mnt/scratch/boxiang/projects/med_translation/processed_data/evaluation/nejm/translation/tmp/wmt18_zh.snt > test.zh
head -n40000 /mnt/scratch/boxiang/projects/med_translation/processed_data/evaluation/nejm/translation/tmp/wmt18_en.snt > test.en


$hunalign -utf -realign -autodict=$out_dir/auto.dic $dictionary \
test.zh \
test.en


$hunalign -utf -realign -batch $out_dir/auto.dic $out_dir/batch

while read line; do
	src=$(echo "$line" | cut -f1)
	tgt=$(echo "$line" | cut -f2)
	ladder=$(echo "$line" | cut -f3)
	
	src=${src/$out_dir/$in_dir}
	src=${src/input/}
	tgt=${tgt/$out_dir/$in_dir}
	tgt=${tgt/input/}

	echo Source: $src 
	echo Target: $tgt
	echo Alignment: $ladder

	bitext=${ladder/.ladder/.bitext}
	python2.7 $ladder2text $ladder $src $tgt > $bitext

done < $out_dir/batch

cat $out_dir/*bitext | cut -f 2 > $out_dir/align.hunalign-s
cat $out_dir/*bitext | cut -f 3 > $out_dir/align.hunalign-t