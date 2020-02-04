#!/usr/bin/env bash
# Author : Thamme Gowda, Modified by Boxiang Liu
# Created : Nov 05, 2019

ONMT=/mnt/home/boxiang/projects/OpenNMT-py
FROM=../processed_data/translation/wmt18/train/
OUT=../processed_data/translation/nejm/train/
TRAIN_DATA=../processed_data/subset/subset/
VALID_DATA=../processed_data/split_data/split_train_test/
BPE_DIR=../processed_data/translation/wmt18/train/data/
python=/mnt/home/boxiang/software/anaconda2/envs/py3/bin/python

for n in 4000 8000 16000 32000 64000 93303; do

echo "Subset of $n sentence pairs."
TRAIN_SRC=$TRAIN_DATA/nejm.train.$n.zh
TRAIN_TGT=$TRAIN_DATA/nejm.train.$n.en
VALID_SRC=$VALID_DATA/nejm.dev.zh
VALID_TGT=$VALID_DATA/nejm.dev.en
# BPE_OPS=90000

echo "Output dir = $OUT"
mkdir -p $OUT/data/$n/{zh2en,en2zh}
mkdir -p $OUT/models/$n/
mkdir -p $OUT/test/$n/

echo "Step 1a: Preprocess inputs"
echo "BPE on source"

$ONMT/tools/apply_bpe.py -c $BPE_DIR/bpe-codes.zh < $TRAIN_SRC > $OUT/data/$n/train.$n.zh
$ONMT/tools/apply_bpe.py -c $BPE_DIR/bpe-codes.zh < $VALID_SRC > $OUT/data/$n/valid.zh
$ONMT/tools/apply_bpe.py -c $BPE_DIR/bpe-codes.en < $TRAIN_TGT > $OUT/data/$n/train.$n.en
$ONMT/tools/apply_bpe.py -c $BPE_DIR/bpe-codes.en < $VALID_TGT > $OUT/data/$n/valid.en


echo "Step 1b: Preprocess"
# zh -> en
$python $ONMT/preprocess.py \
    -src_seq_length 999 \
    -tgt_seq_length 999 \
    -train_src $OUT/data/$n/train.$n.zh \
    -train_tgt $OUT/data/$n/train.$n.en \
    -valid_src $OUT/data/$n/valid.zh \
    -valid_tgt $OUT/data/$n/valid.en \
    -save_data $OUT/data/$n/zh2en/processed \
    -overwrite

# en -> zh
$python $ONMT/preprocess.py \
    -src_seq_length 999 \
    -tgt_seq_length 999 \
    -train_src $OUT/data/$n/train.$n.en \
    -train_tgt $OUT/data/$n/train.$n.zh \
    -valid_src $OUT/data/$n/valid.en \
    -valid_tgt $OUT/data/$n/valid.zh \
    -save_data $OUT/data/$n/en2zh/processed \
    -overwrite


echo "Step 2: Train"
echo "Chinese to English"
echo "Creating hard link for wmt18 baseline model."
ln $FROM/models/zh2en_step_390000.pt $OUT/models/$n/zh2en_step_390000.pt

$python restartsub.py TitanXx8 8 zh2en_${n} \
"$python $ONMT/train.py \
-data $OUT/data/$n/zh2en/processed \
-save_model $OUT/models/$n/zh2en \
-layers 6 \
-rnn_size 512 \
-word_vec_size 512 \
-transformer_ff 2048 \
-heads 8  \
-encoder_type transformer \
-decoder_type transformer \
-position_encoding \
-train_steps 490000 \
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
-gpu_ranks 0 1 2 3 4 5 6 7 \
-world_size 8 \
-seed 42" | \
tee $OUT/models/$n/zh2en_restartsub.log & 


echo "English to Chinese"
echo "Creating hard link for wmt18 baseline model."
ln $FROM/models/en2zh_step_500000.pt $OUT/models/$n/en2zh_step_500000.pt

$python restartsub.py TitanXx8 8 en2zh_${n} \
"$python $ONMT/train.py \
-data $OUT/data/$n/en2zh/processed \
-save_model $OUT/models/$n/en2zh \
-layers 6 \
-rnn_size 512 \
-word_vec_size 512 \
-transformer_ff 2048 \
-heads 8 \
-encoder_type transformer \
-decoder_type transformer \
-position_encoding \
-train_steps 600000 \
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
-gpu_ranks 0 1 2 3 4 5 6 7 \
-world_size 8 \
-seed 42" | \
tee $OUT/models/$n/en2zh_restartsub.log & 


#===== EXPERIMENT END ======
done