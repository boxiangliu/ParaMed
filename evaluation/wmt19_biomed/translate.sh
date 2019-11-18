export onmt=~/projects/OpenNMT-py/onmt/
export data=../data/wmt19_biomed_modified/
export model=../processed_data/translation/wmt18/train_bpe/models/
export ONMT=/mnt/home/boxiang/projects/OpenNMT-py
export moses_scripts=~/software/mosesdecoder/scripts/

# Chinese sentence segmentation by Jieba:
python3 -m jieba -d ' ' < $data/medline_zh2en_zh.textonly.txt \
> $data/medline_zh2en_zh.textonly.tok.txt

# Apply BPE:
$ONMT/tools/apply_bpe.py \
-c ../processed_data/translation/wmt18/train_bpe/data/bpe-codes.joint \
< $data/medline_zh2en_zh.textonly.tok.txt \
> $data/medline_zh2en_zh.textonly.tok.bpe.txt

# Translate to English:
$onmt/bin/translate.py \
	-model $model/zh2en_step_140000.pt \
	-src $data/medline_zh2en_zh.textonly.tok.bpe.txt \
	-output $data/medline_zh2en_zh.textonly.tok.bpe.2en.txt \
	-replace_unk -verbose \
	-gpu 0

# Remove BPE characters:
cat $data/medline_zh2en_zh.textonly.tok.bpe.2en.txt \
| sed -E 's/(@@ )|(@@ ?$)//g' > $data/medline_zh2en_zh.textonly.tok.2en.txt

# Tokenize English:
cat $data/medline_zh2en_en.textonly.txt | \
$moses_scripts/tokenizer/lowercase.perl | \
$moses_scripts/tokenizer/normalize-punctuation.perl -l en | \
$moses_scripts/tokenizer/tokenizer.perl -a -l en \
>> $data/medline_zh2en_en.textonly.tok.txt

# Add document-sentence markers: 
paste -d "|" \
$data/medline_zh2en_zh.textonly.tok.txt \
<(awk 'BEGIN{FS="\t";OFS=","}{print $1,$2}' $data/medline_zh2en_zh.txt) \
> $data/medline_zh2en_zh.textonly.tok.mark.txt

paste -d "|" \
$data/medline_zh2en_en.textonly.tok.txt \
<(awk 'BEGIN{FS="\t";OFS=","}{print $1,$2}' $data/medline_zh2en_en.txt) \
> $data/medline_zh2en_en.textonly.tok.mark.txt


paste -d "|" \
$data/medline_zh2en_zh.textonly.tok.2en.txt \
<(awk 'BEGIN{FS="\t";OFS=","}{print $1,$2}' $data/medline_zh2en_zh.txt) \
> $data/medline_zh2en_zh.textonly.tok.2en.mark.txt


# Split by document:
for doc in `awk '{print $1}' $data/medline_zh2en_zh.txt | uniq`; do
	grep $doc, $data/medline_zh2en_zh.textonly.tok.mark.txt > \
	$data/separate_docs/${doc}_zh.snt

	grep $doc, $data/medline_zh2en_zh.textonly.tok.2en.mark.txt > \
	$data/separate_docs/${doc}_zh.2en
done

for doc in `awk '{print $1}' $data/medline_zh2en_en.txt | uniq`; do
	grep $doc, $data/medline_zh2en_en.textonly.tok.mark.txt > \
	$data/separate_docs/${doc}_en.snt
done