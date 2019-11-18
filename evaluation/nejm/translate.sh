export data=../processed_data/preprocess/sentences
export model=../processed_data/translation/wmt18/train_bpe/models/
export ONMT=~/projects/OpenNMT-py
export moses_scripts=~/software/mosesdecoder/scripts/
export out_dir=../processed_data/evaluation/nejm/translation/
[[ ! -f $out_dir ]] | mkdir -p $out_dir

# Articles:
articles=(鼻咽癌的吉西他滨联合顺铂诱导化疗 \
	饮水可对饮用含糖饮料产生多大程度的对抗作用 \
	帕妥珠单抗和曲妥珠单抗辅助治疗早期HER2阳性乳腺癌)

# Iterate through all articles:
n=0
for article in ${articles[@]}; do
	n=$(($n+1))
	echo Article: $article
	echo Document No.: $n

	# Apply BPE:
	$ONMT/tools/apply_bpe.py \
	-c ../processed_data/translation/wmt18/train_bpe/data/bpe-codes.joint \
	< $data/${article}.zh.tok \
	> $out_dir/${article}.zh.tok.bpe

	# Translate to English:
	$ONMT/onmt/bin/translate.py \
	-model $model/zh2en_step_140000.pt \
	-src $out_dir/${article}.zh.tok.bpe \
	-output $out_dir/${article}.zh.tok.bpe.2en \
	-replace_unk -verbose \
	-gpu 0

	# Remove BPE characters:
	cat $out_dir/${article}.zh.tok.bpe.2en \
	| sed -E 's/(@@ )|(@@ ?$)//g' > $out_dir/${article}.zh.tok.2en

	# Add document-sentence markers:
	awk '{print $0" | doc"v1","NR}' \
	v1=$n $data/${article}.zh.tok > \
	$out_dir/doc${n}_zh.snt

	awk '{print $0" | doc"v1","NR}' \
	v1=$n $data/${article}.en.tok > \
	$out_dir/doc${n}_en.snt

	awk '{print $0" | doc"v1","NR}' \
	v1=$n $out_dir/${article}.zh.tok.2en > \
	$out_dir/doc${n}_zh.2en

done