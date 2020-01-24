in_dir=../processed_data/preprocess/tokenize/
moses_scripts=~/software/mosesdecoder/scripts/
out_dir=../processed_data/preprocess/truecase/
mkdir -p $out_dir

cat $in_dir/*.filt.en > $out_dir/corpus.en

$moses_scripts/recaser/train-truecaser.perl \
-model $out_dir/truecase-model.en -corpus $out_dir/corpus.en

for f in $in_dir/*.filt.en; do
	echo $f
	base=$(basename $f)
	$moses_scripts/recaser/truecase.perl < $f \
	> $out_dir/$base -model $out_dir/truecase-model.en
done
