in_dir=../processed_data/preprocess/manual_align/input/
out_dir=../processed_data/evaluation/nejm/align/hunalign/input/
mkdir -p $out_dir

for a in $in_dir/*; do
	echo $a
	base=$(basename $a)
	# ln $a $out_dir/$base

	stem=${base%.*}
	
	awk '{print $0" | "v1","NR}' \
	v1=$stem $a > \
	$out_dir/$base.mark
done

head -n 40000 /mnt/data/boxiang/wmt18/train/corpus.zh > \
$out_dir/wmt18.zh
head -n 40000 /mnt/data/boxiang/wmt18/train/corpus.en > \
$out_dir/wmt18.en

[[ -f $out_dir/batch ]] && rm $out_dir/batch
for src in $out_dir/*.zh; do
	tgt=${src/.zh/.en}
	out=${src/.zh/.ladder}
	echo -e "$src\t$tgt\t$out" >> $out_dir/batch
done
