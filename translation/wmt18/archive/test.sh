#!/usr/bin/env bash
# Author : Thamme Gowda, Modified by Boxiang Liu
# Created : Nov 05, 2019

ONMT=/mnt/home/boxiang/projects/OpenNMT-py
OUT=../processed_data/translation/wmt18/train_bpe/
DATA=/mnt/data/boxiang/wmt18/
TRAIN_SRC=$DATA/train/corpus.zh
TRAIN_TGT=$DATA/train/corpus.en
VALID_SRC=$DATA/dev/newsdev2017.tc.zh
VALID_TGT=$DATA/dev/newsdev2017.tc.en
BPE_OPS=90000
moses_scripts=~/software/mosesdecoder/scripts/

echo "Output dir = $OUT"
[ -d $OUT ] || mkdir -p $OUT
[ -d $OUT/test ] || mkdir -p  $OUT/test


echo "Step 3: Translate Dev"
model=$OUT/models/zh2en_step_140000.pt
python $ONMT/translate.py -model $model \
    -src $OUT/data/valid.src \
    -output $OUT/test/valid.out \
    -replace_unk -verbose -gpu 0 > $OUT/test/valid.log


echo "BPE decoding/detokenising target to match with references"
mv $OUT/test/valid.out{,.bpe} 
cat $OUT/test/valid.out.bpe | sed -E 's/(@@ )|(@@ ?$)//g' > $OUT/test/valid.out
$moses_scripts/tokenizer/detokenizer.perl -l en < $OUT/test/valid.out > $OUT/test/valid.detok.out
$moses_scripts/tokenizer/detokenizer.perl -l en < $DATA/dev/newsdev2017.tc.en > $DATA/dev/newsdev2017.tc.detok.en

echo "Step 4: Evaluate Dev"
$ONMT/tools/multi-bleu-detok.perl $DATA/dev/newsdev2017.tc.detok.en < $OUT/test/valid.detok.out > $OUT/test/valid.tc.bleu
$ONMT/tools/multi-bleu-detok.perl -lc $DATA/dev/newsdev2017.tc.detok.en < $OUT/test/valid.detok.out > $OUT/test/valid.lc.bleu


python $ONMT/translate.py --model $model \
    --src $OUT/data/valid.src \
    --output $OUT/test/valid.s42_bs1_ml999_lpavg.out \
    --seed 42 \
    --beam_size 1 \
    --max_length 999 \
    --length_penalty avg \
    -replace_unk -verbose -gpu 0 > $OUT/test/valid.s42_bs1_ml999_lpavg.log


python $ONMT/translate.py --model $model \
    --src $OUT/data/valid.src \
    --output $OUT/test/valid.s42_bs5_ml999_lpavg.out \
    --seed 42 \
    --beam_size 5 \
    --max_length 999 \
    --length_penalty avg \
    -replace_unk -verbose -gpu 0 > $OUT/test/valid.s42_bs5_ml999_lpavg.log

python $ONMT/translate.py --model $model \
    --src $OUT/data/valid.src \
    --output $OUT/test/valid.s42_bs10_ml999_lpavg.out \
    --seed 42 \
    --beam_size 10 \
    --max_length 999 \
    --length_penalty avg \
    -replace_unk -verbose -gpu 0 > $OUT/test/valid.s42_bs10_ml999_lpavg.log

python $ONMT/translate.py --model $model \
    --src $OUT/data/valid.src \
    --output $OUT/test/valid.s42_bs15_ml999_lpavg.out \
    --seed 42 \
    --beam_size 15 \
    --max_length 999 \
    --length_penalty avg \
    -replace_unk -verbose -gpu 0 > $OUT/test/valid.s42_bs15_ml999_lpavg.log

$moses_scripts/tokenizer/detokenizer.perl -l en < $DATA/dev/newsdev2017.tc.en > $DATA/dev/newsdev2017.tc.detok.en

for i in s42_bs1_ml999_lpavg s42_bs5_ml999_lpavg s42_bs10_ml999_lpavg s42_bs15_ml999_lpavg; do
echo "BPE decoding/detokenising target to match with references"
mv $OUT/test/valid.$i.out{,.bpe} 
cat $OUT/test/valid.$i.out.bpe | sed -E 's/(@@ )|(@@ ?$)//g' > $OUT/test/valid.$i.out
$moses_scripts/tokenizer/detokenizer.perl -l en < $OUT/test/valid.$i.out > $OUT/test/valid.detok.$i.out

echo "Step 4: Evaluate Dev"
$ONMT/tools/multi-bleu-detok.perl $DATA/dev/newsdev2017.tc.detok.en < $OUT/test/valid.detok.$i.out > $OUT/test/valid.tc.$i.bleu
$ONMT/tools/multi-bleu-detok.perl -lc $DATA/dev/newsdev2017.tc.detok.en < $OUT/test/valid.detok.$i.out > $OUT/test/valid.lc.$i.bleu
done

