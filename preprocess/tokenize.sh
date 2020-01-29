data=../processed_data/preprocess/sentences/eserix/
moses_scripts=~/software/mosesdecoder/scripts/
out_dir=../processed_data/preprocess/tokenize/
mkdir -p $out_dir

src=zh
tgt=en

for article in `ls $data/*.$tgt`; do
	echo $article
	base=$(basename $article)
	cat $article | \
	$moses_scripts/tokenizer/tokenizer.perl -a -l $tgt  \
	> $out_dir/$base
done

for article in `ls $data/*.$src`; do
	echo $article
	base=$(basename $article)
	python3 -m jieba -d ' ' < $article \
	> $out_dir/$base
done