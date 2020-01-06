#!/bin/bash
ONMT=/mnt/home/boxiang/projects/OpenNMT-py
WMT18=/mnt/home/baigong/scratch_SMT/seqtoseq/mymodels/ # Path to the WMT18 baseline model.
NEJM=../processed_data/translation/nejm/baigong/train/ # Path to model fine-tuned on NEJM.
VALID=../processed_data/clean/ # Path to NEJM valid set.
moses_scripts=~/software/mosesdecoder/scripts/

# detokenize 
models=($WMT18/zh2en/bpe/model_step_370000.pt \
	$NEJM/models/zh2en_step_480000.bak.pt)
srcs=($NEJM/data/valid.src \
	$NEJM/data/valid.src)
tgts=($VALID/nejm.valid.en \
	$VALID/nejm.valid.en)
translations=(wmt18.zh2en nejm.zh2en)

for i in {0..1}; do
	model=${models[$i]}
	src=${srcs[$i]}
	tgt=${tgts[$i]}
	translation=${translations[$i]}

	echo "Translate $translation"
	python $ONMT/translate.py \
		-batch_size 1 \
		-model $model \
		-src $src \
		-output $NEJM/test/$translation \
		-replace_unk -verbose \
		-gpu 0 > $NEJM/test/${translation}.log


	echo "BPE decoding/detokenising target to match with references"
	mv $NEJM/test/$translation{,.bpe}
	cat $NEJM/test/$translation.bpe | sed -E 's/(@@ )|(@@ ?$)//g' > $NEJM/test/$translation
	echo $NEJM/test/$translation

	$ONMT/tools/multi-bleu.perl -lc $tgt < $NEJM/test/$translation > $NEJM/test/$translation.lc.bleu
	$ONMT/tools/multi-bleu.perl $tgt < $NEJM/test/$translation > $NEJM/test/$translation.tc.bleu

	# echo "Evaluate $translation"
	# if [[ $NEJM/test/$translation == *"zh2en" ]]; then
	# 	mv $NEJM/test/$translation{,.tok}
	# 	$moses_scripts/tokenizer/detokenizer.perl -l en < $NEJM/test/$translation.tok > $NEJM/test/$translation

	# 	$ONMT/tools/multi-bleu-detok.perl $tgt < \
	# 		$NEJM/test/$translation > $NEJM/test/$translation.tc.bleu
	# 	$ONMT/tools/multi-bleu-detok.perl -lc $tgt < \
	# 		$NEJM/test/$translation > $NEJM/test/$translation.lc.bleu
	# else
	# 	$ONMT/tools/multi-bleu-detok.perl $tgt < \
	# 		$NEJM/test/$translation > $NEJM/test/$translation.tc.bleu
	# 	$ONMT/tools/multi-bleu-detok.perl -lc $tgt < \
	# 		$NEJM/test/$translation > $NEJM/test/$translation.lc.bleu
	# fi

done
