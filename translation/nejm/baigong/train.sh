#!/usr/bin/env bash
# Author : Thamme Gowda, Modified by Boxiang Liu
# Created : Nov 05, 2019

ONMT=/mnt/home/boxiang/projects/OpenNMT-py
OUT=../processed_data/translation/nejm/baigong/train/
TRAIN_DATA=../processed_data/subset/subset/
VALID_DATA=../processed_data/clean/
BPE_DIR=/mnt/home/baigong/data/wmt18zh-en/org/
python=/mnt/home/boxiang/software/anaconda2/envs/py3/bin/python

for n in 4000 8000 16000 32000 64000 90861; do

echo "Subset of $n sentence pairs."
TRAIN_SRC=$TRAIN_DATA/nejm.train.$n.zh
TRAIN_TGT=$TRAIN_DATA/nejm.train.$n.en
VALID_SRC=$VALID_DATA/nejm.valid.zh
VALID_TGT=$VALID_DATA/nejm.valid.en
# BPE_OPS=90000

echo "Output dir = $OUT"
mkdir -p $OUT/data/$n/{zh2en,en2zh}
mkdir -p $OUT/models/$n/
mkdir -p $OUT/test/$n/

echo "Step 1a: Preprocess inputs"
echo "BPE on source"

$ONMT/tools/apply_bpe.py -c $BPE_DIR/bpe_dict.zh < $TRAIN_SRC > $OUT/data/$n/train.$n.src
$ONMT/tools/apply_bpe.py -c $BPE_DIR/bpe_dict.zh < $VALID_SRC > $OUT/data/$n/valid.src
$ONMT/tools/apply_bpe.py -c $BPE_DIR/bpe_dict.en < $TRAIN_TGT > $OUT/data/$n/train.$n.tgt
$ONMT/tools/apply_bpe.py -c $BPE_DIR/bpe_dict.en < $VALID_TGT > $OUT/data/$n/valid.tgt


echo "Step 1b: Preprocess"
# zh -> en
python $ONMT/preprocess.py \
    -src_seq_length 999 \
    -tgt_seq_length 999 \
    -train_src $OUT/data/$n/train.$n.src \
    -train_tgt $OUT/data/$n/train.$n.tgt \
    -valid_src $OUT/data/$n/valid.src \
    -valid_tgt $OUT/data/$n/valid.tgt \
    -save_data $OUT/data/$n/zh2en/processed \
    -overwrite

# en -> zh
python $ONMT/preprocess.py \
    -src_seq_length 999 \
    -tgt_seq_length 999 \
    -train_src $OUT/data/$n/train.$n.tgt \
    -train_tgt $OUT/data/$n/train.$n.src \
    -valid_src $OUT/data/$n/valid.tgt \
    -valid_tgt $OUT/data/$n/valid.src \
    -save_data $OUT/data/$n/en2zh/processed \
    -overwrite


echo "Step 2: Train"

# sub TitanXx8 8 nejm_${n} \
$python restartsub.py TitanXx8 8 nejm_${n} \
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
-gpu_ranks 0 1 2 3 4 5 6 7 \
-world_size 8 \
-master_port 10003" | \
tee $OUT/models/$n/zh2en_restartsub.log & 
# \
# -train_from /mnt/home/baigong/scratch_SMT/seqtoseq/mymodels/zh2en/bpe/model_step_370000.pt" \
# $OUT/models/$n/zh2en.log


# python $ONMT/train.py \
# -data $OUT/data/en2zh/processed \
# -save_model $OUT/models/en2zh \
# -layers 6 \
# -rnn_size 512 \
# -word_vec_size 512 \
# -transformer_ff 2048 \
# -heads 8  \
# -encoder_type transformer \
# -decoder_type transformer \
# -position_encoding \
# -train_steps 300000 \
# -max_generator_batches 2 \
# -dropout 0.1 \
# -batch_size 4096 \
# -batch_type tokens \
# -normalization tokens \
# -accum_count 2 \
# -optim adam \
# -adam_beta2 0.998 \
# -decay_method noam \
# -warmup_steps 8000 \
# -learning_rate 2 \
# -max_grad_norm 0 \
# -param_init 0 \
# -param_init_glorot \
# -label_smoothing 0.1 \
# -valid_steps 10000 \
# -save_checkpoint_steps 10000 \
# -world_size 8 \
# -gpu_ranks 0 1 2 3 4 5 6 7 \
# -train_from "../processed_data/translation/\
# wmt18/train_bpe/models/en2zh_step_200000.pt" \
# &> $OUT/models/en2zh.log

#===== EXPERIMENT END ======
done