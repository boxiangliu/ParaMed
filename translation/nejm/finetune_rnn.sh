#!/usr/bin/env bash
# Author : Thamme Gowda, Modified by Boxiang Liu
# Created : Nov 05, 2019

ONMT=/mnt/home/boxiang/projects/OpenNMT-py
FROM=../processed_data/translation/wmt18/train_rnn/
OUT=../processed_data/translation/nejm/finetune_rnn/
TRAIN_DATA=../processed_data/subset/subset/
VALID_DATA=../processed_data/split_data/split_train_test/
BPE_DIR=../processed_data/translation/wmt18/train_rnn/data/
python=/mnt/home/boxiang/software/anaconda2/envs/py3/bin/python

for n in 4000 8000 16000 32000 64000 93303; do

echo "Subset of $n sentence pairs."
TRAIN_SRC=$TRAIN_DATA/nejm.train.$n.zh
TRAIN_TGT=$TRAIN_DATA/nejm.train.$n.en
VALID_SRC=$VALID_DATA/nejm.dev.zh
VALID_TGT=$VALID_DATA/nejm.dev.en
TEST_SRC=$VALID_DATA/nejm.test.zh
TEST_TGT=$VALID_DATA/nejm.test.en


echo "Output dir = $OUT"
mkdir -p $OUT/data/$n/{zh2en,en2zh}
mkdir -p $OUT/models/$n/
mkdir -p $OUT/test/$n/

echo "Step 1a: Preprocess inputs"
echo "BPE on source"

$ONMT/tools/apply_bpe.py -c $BPE_DIR/bpe-codes.zh < $TRAIN_SRC > $OUT/data/$n/train.$n.zh
$ONMT/tools/apply_bpe.py -c $BPE_DIR/bpe-codes.zh < $VALID_SRC > $OUT/data/$n/valid.zh
$ONMT/tools/apply_bpe.py -c $BPE_DIR/bpe-codes.zh < $TEST_SRC > $OUT/data/$n/test.zh
$ONMT/tools/apply_bpe.py -c $BPE_DIR/bpe-codes.en < $TRAIN_TGT > $OUT/data/$n/train.$n.en
$ONMT/tools/apply_bpe.py -c $BPE_DIR/bpe-codes.en < $VALID_TGT > $OUT/data/$n/valid.en
$ONMT/tools/apply_bpe.py -c $BPE_DIR/bpe-codes.en < $TEST_TGT > $OUT/data/$n/test.en

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
ln $FROM/models/zh2en_step_80000.pt $OUT/models/$n/zh2en_step_80000.pt

$python restartsub.py V100_DGX 1 zh2en_${n} \
"$python $ONMT/train.py \
-data $OUT/data/$n/zh2en/processed \
-save_model $OUT/models/$n/zh2en \
-layers 1 \
-rnn_type LSTM \
-rnn_size 512 \
-word_vec_size 512 \
-train_steps 100000 \
-batch_size 4000 \
-batch_type tokens \
-normalization tokens \
-optim adam \
-learning_rate 0.001 \
-label_smoothing 0.1 \
-valid_steps 2000 \
-save_checkpoint_steps 2000 \
-world_size 1 \
-gpu_ranks 0 \
-seed 42" | \
tee $OUT/models/$n/zh2en_restartsub.log & 


echo "English to Chinese"
echo "Creating hard link for wmt18 baseline model."
ln $FROM/models/en2zh_step_80000.pt $OUT/models/$n/en2zh_step_80000.pt

$python restartsub.py V100_DGX 1 en2zh_${n} \
"$python $ONMT/train.py \
-data $OUT/data/$n/en2zh/processed \
-save_model $OUT/models/$n/en2zh \
-layers 1 \
-rnn_type LSTM \
-rnn_size 512 \
-word_vec_size 512 \
-train_steps 100000 \
-batch_size 4000 \
-batch_type tokens \
-normalization tokens \
-optim adam \
-learning_rate 0.001 \
-label_smoothing 0.1 \
-valid_steps 2000 \
-save_checkpoint_steps 2000 \
-world_size 1 \
-gpu_ranks 0 \
-seed 42" | \
tee $OUT/models/$n/en2zh_restartsub.log & 


#===== EXPERIMENT END ======
done