data=../processed_data/preprocess/tokenize/
moses_scripts=~/software/mosesdecoder/scripts/
out_dir=../processed_data/preprocess/lowercase/
mkdir -p $out_dir

for article in $data/*; do
	echo $article
	base=$(basename $article)
	cat $article | \
	$moses_scripts/tokenizer/lowercase.perl \
	> $out_dir/$base
done