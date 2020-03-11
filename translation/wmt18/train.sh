#!/usr/bin/env bash
# Author : Thamme Gowda, Modified by Boxiang Liu
# Created : Nov 05, 2019
ONMT=/mnt/home/boxiang/projects/OpenNMT-py
OUT=../processed_data/translation/wmt18/train/
DATA=/mnt/data/boxiang/wmt18/
SRC=zh
TGT=en
TRAIN=$DATA/train/corpus
VALID=$DATA/dev/newsdev2017.tc
TEST=$DATA/dev/newstest2017.tc

BPE_OPS=16000
moses_scripts=~/software/mosesdecoder/scripts/

echo "Output dir = $OUT"
[ -d $OUT ] || mkdir -p $OUT
[ -d $OUT/data ] || mkdir -p $OUT/data/{zh2en,en2zh}
[ -d $OUT/models ] || mkdir -p $OUT/models/{zh2en,en2zh}
[ -d $OUT/test ] || mkdir -p  $OUT/test/{zh2en,en2zh}


echo "Step 1a: Preprocess inputs"
echo "BPE on source"
$ONMT/tools/learn_bpe.py -v -s $BPE_OPS < $TRAIN.$SRC > $OUT/data/bpe-codes.$SRC
$ONMT/tools/learn_bpe.py -v -s $BPE_OPS < $TRAIN.$TGT > $OUT/data/bpe-codes.$TGT

$ONMT/tools/apply_bpe.py -c $OUT/data/bpe-codes.$SRC < $TRAIN.$SRC > $OUT/data/train.src
$ONMT/tools/apply_bpe.py -c $OUT/data/bpe-codes.$SRC < $VALID.$SRC > $OUT/data/valid.src
$ONMT/tools/apply_bpe.py -c $OUT/data/bpe-codes.$TGT < $TRAIN.$TGT > $OUT/data/train.tgt
$ONMT/tools/apply_bpe.py -c $OUT/data/bpe-codes.$TGT < $VALID.$TGT > $OUT/data/valid.tgt

#: <<EOF
echo "Step 1b: Preprocess"
# zh -> en
python $ONMT/preprocess.py \
    -src_seq_length 999 \
    -tgt_seq_length 999 \
    -train_src $OUT/data/train.src \
    -train_tgt $OUT/data/train.tgt \
    -valid_src $OUT/data/valid.src \
    -valid_tgt $OUT/data/valid.tgt \
    -save_data $OUT/data/zh2en/processed

# en -> zh
python $ONMT/preprocess.py \
    -src_seq_length 999 \
    -tgt_seq_length 999 \
    -train_src $OUT/data/train.tgt \
    -train_tgt $OUT/data/train.src \
    -valid_src $OUT/data/valid.tgt \
    -valid_tgt $OUT/data/valid.src \
    -save_data $OUT/data/en2zh/processed


echo "Step 2: Train"

python restartsub.py TitanXx8 8 zh2en \
"python $ONMT/train.py \
-data $OUT/data/zh2en/processed \
-save_model $OUT/models/zh2en \
-layers 6 \
-rnn_size 512 \
-word_vec_size 512 \
-transformer_ff 2048 \
-heads 8  \
-encoder_type transformer \
-decoder_type transformer \
-position_encoding \
-train_steps 500000 \
-max_generator_batches 2 \
-dropout 0.1 \
-batch_size 4000 \
-batch_type tokens \
-normalization tokens \
-accum_count 2 \
-optim adam \
-adam_beta2 0.997 \
-decay_method noam \
-warmup_steps 10000 \
-learning_rate 2 \
-max_grad_norm 0 \
-param_init 0 \
-param_init_glorot \
-label_smoothing 0.1 \
-valid_steps 10000 \
-save_checkpoint_steps 5000 \
-world_size 8 \
-gpu_ranks 0 1 2 3 4 5 6 7 \
-master_port 10003"


python restartsub.py TitanXx8 8 en2zh \
"python $ONMT/train.py \
-data $OUT/data/en2zh/processed \
-save_model $OUT/models/en2zh \
-layers 6 \
-rnn_size 512 \
-word_vec_size 512 \
-transformer_ff 2048 \
-heads 8  \
-encoder_type transformer \
-decoder_type transformer \
-position_encoding \
-train_steps 500000 \
-max_generator_batches 2 \
-dropout 0.1 \
-batch_size 2000 \
-batch_type tokens \
-normalization tokens \
-accum_count 2 \
-optim adam \
-adam_beta2 0.997 \
-decay_method noam \
-warmup_steps 10000 \
-learning_rate 2 \
-max_grad_norm 0 \
-param_init 0 \
-param_init_glorot \
-label_smoothing 0.1 \
-valid_steps 10000 \
-save_checkpoint_steps 5000 \
-world_size 8 \
-gpu_ranks 0 1 2 3 4 5 6 7 \
-master_port 10004"