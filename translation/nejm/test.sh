#!/bin/bash

ONMT=/mnt/home/boxiang/projects/OpenNMT-py
WMT18=../processed_data/translation/wmt18/train_bpe/
NEJM=../processed_data/translation/nejm/train/
VALID=../processed_data/preprocess/alignment/
moses_scripts=~/software/mosesdecoder/scripts/

# detokenize 
models=($WMT18/models/zh2en_step_140000.pt \
	$NEJM/models/zh2en_step_300000.pt \
	$WMT18/models/en2zh_step_200000.pt \
	$NEJM/models/en2zh_step_300000.pt)
srcs=($NEJM/data/valid.src $NEJM/data/valid.src \
	$NEJM/data/valid.tgt $NEJM/data/valid.tgt)
tgts=($VALID/nejm_valid.parallel.en $VALID/nejm_valid.parallel.en \
	$VALID/nejm_valid.parallel.zh $VALID/nejm_valid.parallel.zh)
files=(wmt18.zh2en nejm.zh2en wmt18.en2zh nejm.en2zh)

for i in {0..3}; do
	model=${models[$i]}
	src=${srcs[$i]}
	tgt=${tgts[$i]}
	file=${files[$i]}

	# echo "Translate $file"
	# python $ONMT/translate.py \
	# 	-batch_size 1 \
	# 	-model $model \
	#     -src $src \
	#     -output $NEJM/test/$file \
	#     -replace_unk -verbose \
	#     -gpu 0 > $NEJM/test/${file}.log


	echo "BPE decoding/detokenising target to match with references"
	mv $NEJM/test/$file{,.bpe}
	cat $NEJM/test/$file.bpe | sed -E 's/(@@ )|(@@ ?$)//g' > $NEJM/test/$file

	echo "Evaluate $file"
	if [[ $NEJM/test/$file == *"zh2en" ]]; then
		mv $NEJM/test/$file{,.tok}
		$moses_scripts/tokenizer/detokenizer.perl -l en < $NEJM/test/$file.tok > $NEJM/test/$file

		$ONMT/tools/multi-bleu-detok.perl $tgt < \
			$NEJM/test/$file > $NEJM/test/$file.tc.bleu
		$ONMT/tools/multi-bleu-detok.perl -lc $tgt < \
			$NEJM/test/$file > $NEJM/test/$file.lc.bleu
	else
		$ONMT/tools/multi-bleu-detok.perl $tgt < \
			$NEJM/test/$file > $NEJM/test/$file.tc.bleu
		$ONMT/tools/multi-bleu-detok.perl -lc $tgt < \
			$NEJM/test/$file > $NEJM/test/$file.lc.bleu
	fi

done
