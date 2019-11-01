data=~/projects/med_translation/processed_data/crawler/nejm/sentences_concat/
moses_scripts=~/software/mosesdecoder/scripts/

src=zh
tgt=en

cat $data/nejm.$tgt | \
$moses_scripts/tokenizer/lowercase.perl | \
$moses_scripts/tokenizer/normalize-punctuation.perl -l $tgt | \
$moses_scripts/tokenizer/tokenizer.perl -a -l $tgt  \
> $data/nejm.tok.$tgt

python3 -m jieba -d ' ' < $data/nejm.$src \
> $data/nejm.tok.$src