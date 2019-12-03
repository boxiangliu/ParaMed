export data=../processed_data/preprocess/sentences
export model=../processed_data/translation/wmt18/train_bpe/models/
export ONMT=~/projects/OpenNMT-py
export moses_scripts=~/software/mosesdecoder/scripts/
export out_dir=../processed_data/evaluation/nejm/translation/
[[ ! -f $out_dir ]] | mkdir -p $out_dir

# Articles:
articles=(鼻咽癌的吉西他滨联合顺铂诱导化疗 \
	饮水可对饮用含糖饮料产生多大程度的对抗作用 \
	帕妥珠单抗和曲妥珠单抗辅助治疗早期HER2阳性乳腺癌 \
	转移性去势抵抗性前列腺癌的恩杂鲁胺耐药 \
	婴儿B群链球菌疾病预防指南更新 \
	黑种人理发店可帮助顾客降血压 \
	内科患者应用阿哌沙班和依诺肝素预防血栓形成的比较 \
	尼拉帕尼用于铂类敏感型复发性卵巢癌的维持治疗 \
	膀胱切除术的最佳手术方法：开放式手术与机器人辅助手术的比较 \
	1型糖尿病患者胰岛素治疗中加用sotagliflozin的效果 \
	HIV相关癌症和疾病 \
	2017年慢性阻塞性肺疾病诊断和治疗的GOLD指南)

# Iterate through all articles:
n=0
for article in ${articles[@]}; do
	n=$(($n+1))
	echo Article: $article
	echo Document No.: $n

	## zh => en ##
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
	-batch_size 1 \
	-gpu 0

	# Remove BPE characters:
	cat $out_dir/${article}.zh.tok.bpe.2en \
	| sed -E 's/(@@ )|(@@ ?$)//g' > $out_dir/${article}.zh.tok.2en


	# en => zh
	# Apply BPE:
	$ONMT/tools/apply_bpe.py \
	-c ../processed_data/translation/wmt18/train_bpe/data/bpe-codes.joint \
	< $data/${article}.en.tok \
	> $out_dir/${article}.en.tok.bpe

	# Translate to Chinese:
	$ONMT/onmt/bin/translate.py \
	-model $model/en2zh_step_200000.pt \
	-src $out_dir/${article}.en.tok.bpe \
	-output $out_dir/${article}.en.tok.bpe.2zh \
	-replace_unk -verbose \
	-batch_size 1 \
	-gpu 0

	# Remove BPE characters:
	cat $out_dir/${article}.en.tok.bpe.2zh \
	| sed -E 's/(@@ )|(@@ ?$)//g' > $out_dir/${article}.en.tok.2zh


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

	awk '{print $0" | doc"v1","NR}' \
	v1=$n $out_dir/${article}.en.tok.2zh > \
	$out_dir/doc${n}_en.2zh

	rm $out_dir/$article*
done