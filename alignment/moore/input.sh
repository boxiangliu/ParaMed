data=../processed_data/preprocess/truecase/
out_dir=../processed_data/alignment/moore/input/
mkdir -p $out_dir/


# Link NEJM articles:
for f in $data/*; do
	echo $f
	base=$(basename $f)

	# Check if file is not empty:
	if [[ -s $f ]]; then
		base=${base/.filt./_}.snt
		ln $f $out_dir/$base
	fi
done

# Adding parallel corpora for IBM 1 model construction.
head -n 100000 /mnt/data/boxiang/wmt18/train/corpus.zh > \
$out_dir/wmt18_zh.snt
head -n 100000 /mnt/data/boxiang/wmt18/train/corpus.en > \
$out_dir/wmt18_en.snt