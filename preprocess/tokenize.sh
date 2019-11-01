data=../processed_data/crawler/nejm/sentences/
moses_scripts=~/software/mosesdecoder/scripts/

src=zh
tgt=en

for article in `ls $data/*.$tgt`; do
	echo $article
	cat $article | \
	$moses_scripts/tokenizer/lowercase.perl | \
	$moses_scripts/tokenizer/normalize-punctuation.perl -l $tgt | \
	$moses_scripts/tokenizer/tokenizer.perl -a -l $tgt  \
	> $article.tok
done

for article in `ls $data/*.$src`; do
	echo $article
	python3 -m jieba -d ' ' < $article \
	> $article.tok
done