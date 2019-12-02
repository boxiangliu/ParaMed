
ONMT=/mnt/home/boxiang/projects/OpenNMT-py
WMT18=../processed_data/translation/wmt18/train_bpe/
NEJM=../processed_data/translation/nejm/train/
DATA=../processed_data/alignment/moore/align/
BPE_DIR=../processed_data/translation/wmt18/train_bpe/data/
TRAIN_SRC=$DATA/nejm.zh
TRAIN_TGT=$DATA/nejm.en
VALID_SRC=../processed_data/preprocess/alignment/nejm_valid.parallel.zh
VALID_TGT=../processed_data/preprocess/alignment/nejm_valid.parallel.en


models=($WMT18/models/zh2en_step_140000.pt \
	$NEJM/models/zh2en_step_300000.pt \
	$WMT18/models/en2zh_step_200000.pt \
	$NEJM/models/en2zh_step_300000.pt)
srcs=($NEJM/data/valid.src $NEJM/data/valid.src \
	$NEJM/data/valid.tgt $NEJM/data/valid.tgt)
tgts=($NEJM/data/valid.tgt $NEJM/data/valid.tgt \
	$NEJM/data/valid.src $NEJM/data/valid.src)
files=(wmt18.zh2en nejm.zh2en wmt18.en2zh nejm.en2zh)

for i in {0..3}; do
	model=${models[$i]}
	src=${srcs[$i]}
	tgt=${tgts[$i]}
	file=${files[$i]}

	echo "Translate $file"
	python $ONMT/translate.py \
		-batch_size 1 \
		-model $model \
	    -src $src \
	    -output $OUT/test/$file \
	    -replace_unk -verbose \
	    -gpu 0 > $OUT/test/${file}.log


	echo "BPE decoding/detokenising target to match with references"
	mv $OUT/test/$file{,.bpe}
	cat $OUT/test/$file.bpe | sed -E 's/(@@ )|(@@ ?$)//g' > $OUT/test/$file


	echo "Evaluate $file"
	$ONMT/tools/multi-bleu-detok.perl $tgt < \
		$OUT/test/$file > $OUT/test/$file.bleu
	$ONMT/tools/multi-bleu-detok.perl -lc $tgt < \
		$OUT/test/$file > $OUT/test/$file.bleu
done
