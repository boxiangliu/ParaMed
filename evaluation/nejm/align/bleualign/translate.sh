export data=../processed_data/preprocess/manual_align/input/
export model=../processed_data/translation/wmt18/train/models/
export ONMT=~/projects/OpenNMT-py
export moses_scripts=~/software/mosesdecoder/scripts/
export out_dir=../processed_data/evaluation/nejm/align/bleualign/translate/
mkdir -p $out_dir

# Iterate through all articles:
for f in $data/doc*; do
	echo $f
	base=$(basename $f)
	ln $f $out_dir/$base
done

n=0
for zh in $out_dir/doc*.zh; do
	n=$(($n+1))
	en=${zh/.zh/.en}
	echo Chinese Article: $zh
	echo English Article: $en
	echo Document No.: $n

	## zh => en ##
	# Apply BPE:
	$ONMT/tools/apply_bpe.py \
	-c ../processed_data/translation/wmt18/train/data/bpe-codes.zh \
	< $zh \
	> $zh.bpe

	# Translate to English:
	$ONMT/onmt/bin/translate.py \
	-model $model/zh2en_step_270000.pt \
	-src $zh.bpe \
	-output $zh.bpe.2en \
	-replace_unk -verbose \
	-batch_size 1 \
	-gpu 0

	# Remove BPE characters:
	cat $zh.bpe.2en \
	| sed -E 's/(@@ )|(@@ ?$)//g' > $zh.2en


	# en => zh
	# Apply BPE:
	$ONMT/tools/apply_bpe.py \
	-c ../processed_data/translation/wmt18/train/data/bpe-codes.en \
	< $en \
	> $en.bpe

	# Translate to Chinese:
	$ONMT/onmt/bin/translate.py \
	-model $model/en2zh_step_410000.pt \
	-src $en.bpe \
	-output $en.bpe.2zh \
	-replace_unk -verbose \
	-batch_size 1 \
	-gpu 0

	# Remove BPE characters:
	cat $en.bpe.2zh \
	| sed -E 's/(@@ )|(@@ ?$)//g' > $en.2zh

done
rm $out_dir/*bpe*