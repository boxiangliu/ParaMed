#!/usr/bin/env bash
# Author : Thamme Gowda, Modified by Boxiang Liu
# Created : Nov 05, 2019

ONMT=/mnt/home/boxiang/projects/OpenNMT-py
OUT=../processed_data/translation/nejm/baigong/train/
DATA=../processed_data/clean/
BPE_DIR=/mnt/home/baigong/data/wmt18zh-en/org/
TRAIN_SRC=$DATA/nejm.train.zh
TRAIN_TGT=$DATA/nejm.train.en
VALID_SRC=$DATA/nejm.valid.zh
VALID_TGT=$DATA/nejm.valid.en
# BPE_OPS=90000

echo "Output dir = $OUT"
[ -d $OUT ] || mkdir -p $OUT
[ -d $OUT/data ] || mkdir -p $OUT/data/{zh2en,en2zh}
[ -d $OUT/models ] || mkdir $OUT/models
[ -d $OUT/test ] || mkdir -p  $OUT/test


echo "Step 1a: Preprocess inputs"
echo "BPE on source"

$ONMT/tools/apply_bpe.py -c $BPE_DIR/bpe_dict.zh < $TRAIN_SRC > $OUT/data/train.src
$ONMT/tools/apply_bpe.py -c $BPE_DIR/bpe_dict.zh < $VALID_SRC > $OUT/data/valid.src
$ONMT/tools/apply_bpe.py -c $BPE_DIR/bpe_dict.en < $TRAIN_TGT > $OUT/data/train.tgt
$ONMT/tools/apply_bpe.py -c $BPE_DIR/bpe_dict.en < $VALID_TGT > $OUT/data/valid.tgt

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
    -save_data $OUT/data/zh2en/processed \
    -overwrite

# en -> zh
python $ONMT/preprocess.py \
    -src_seq_length 999 \
    -tgt_seq_length 999 \
    -train_src $OUT/data/train.tgt \
    -train_tgt $OUT/data/train.src \
    -valid_src $OUT/data/valid.tgt \
    -valid_tgt $OUT/data/valid.src \
    -save_data $OUT/data/en2zh/processed \
    -overwrite


echo "Step 2: Train"

python $ONMT/train.py \
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
-train_steps 700000 \
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
-param_init 0  \
-param_init_glorot \
-label_smoothing 0.1 \
-valid_steps 10000 \
-save_checkpoint_steps 10000 \
-gpu_ranks 0 1 2 3 4 5 6 7 \
-world_size 8 \
-master_port 10003 \
-keep_checkpoint 10 \
-train_from /mnt/home/baigong/scratch_SMT/seqtoseq/mymodels/zh2en/bpe/model_step_370000.pt \
&> $OUT/models/zh2en.log


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