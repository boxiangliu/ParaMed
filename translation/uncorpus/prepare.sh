data=~/projects/med_translation/data/uncorpus/
moses_scripts=~/software/mosesdecoder/scripts/

src=zh
tgt=en

cat $data/en-zh/UNv1.0.en-zh.$tgt | \
$moses_scripts/tokenizer/lowercase.perl | \
$moses_scripts/tokenizer/normalize-punctuation.perl -l $tgt | \
$moses_scripts/tokenizer/tokenizer.perl -a -l $tgt  \
>> $data/en-zh/UNv1.0.en-zh.tok.$tgt

python3 -m jieba -d ' ' < $data/en-zh/UNv1.0.en-zh.$src \
>> $data/en-zh/UNv1.0.en-zh.tok.$src