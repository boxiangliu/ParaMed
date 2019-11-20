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

echo "Output dir = $OUT"
[ -d $OUT ] || mkdir -p $OUT
[ -d $OUT/data ] || mkdir -p $OUT/data/{zh2en,en2zh}
[ -d $OUT/models ] || mkdir $OUT/models
[ -d $OUT/test ] || mkdir -p  $OUT/test


echo "Step 1a: Preprocess inputs"
echo "BPE on source"
cat $TRAIN_SRC $TRAIN_TGT > ${TRAIN_SRC/.zh/.joint}
$ONMT/tools/learn_bpe.py -s $BPE_OPS < ${TRAIN_SRC/.zh/.joint} > $OUT/data/bpe-codes.joint
$ONMT/tools/apply_bpe.py -c $OUT/data/bpe-codes.joint < $TRAIN_SRC > $OUT/data/train.src
$ONMT/tools/apply_bpe.py -c $OUT/data/bpe-codes.joint < $VALID_SRC > $OUT/data/valid.src
$ONMT/tools/apply_bpe.py -c $OUT/data/bpe-codes.joint < $TRAIN_TGT > $OUT/data/train.tgt
$ONMT/tools/apply_bpe.py -c $OUT/data/bpe-codes.joint < $VALID_TGT > $OUT/data/valid.tgt

#: <<EOF
echo "Step 1b: Preprocess"
# zh -> en
python $ONMT/preprocess.py \
    -src_seq_length 256 \
    -tgt_seq_length 256 \
    -train_src $OUT/data/train.src \
    -train_tgt $OUT/data/train.tgt \
    -valid_src $OUT/data/valid.src \
    -valid_tgt $OUT/data/valid.tgt \
    -save_data $OUT/data/zh2en/processed

# en -> zh
python $ONMT/preprocess.py \
    -src_seq_length 256 \
    -tgt_seq_length 256 \
    -train_src $OUT/data/train.tgt \
    -train_tgt $OUT/data/train.src \
    -valid_src $OUT/data/valid.tgt \
    -valid_tgt $OUT/data/valid.src \
    -save_data $OUT/data/en2zh/processed


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
-train_steps 200000 \
-max_generator_batches 2 \
-dropout 0.1 \
-batch_size 4096 \
-batch_type tokens \
-normalization tokens \
-accum_count 2 \
-optim adam \
-adam_beta2 0.998 \
-decay_method noam \
-warmup_steps 8000 \
-learning_rate 2 \
-max_grad_norm 0 \
-param_init 0 \
-param_init_glorot \
-label_smoothing 0.1 \
-valid_steps 10000 \
-save_checkpoint_steps 10000 \
-world_size 8 \
-gpu_ranks 0 1 2 3 4 5 6 7 \
&> $OUT/models/zh2en.log


python $ONMT/train.py \
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
-train_steps 200000 \
-max_generator_batches 2 \
-dropout 0.1 \
-batch_size 4096 \
-batch_type tokens \
-normalization tokens \
-accum_count 2 \
-optim adam \
-adam_beta2 0.998 \
-decay_method noam \
-warmup_steps 8000 \
-learning_rate 2 \
-max_grad_norm 0 \
-param_init 0 \
-param_init_glorot \
-label_smoothing 0.1 \
-valid_steps 10000 \
-save_checkpoint_steps 10000 \
-world_size 8 \
-gpu_ranks 0 1 2 3 4 5 6 7\
&> $OUT/models/en2zh.log

python restartsub.py M40x8 8 en2zh "python $ONMT/train.py \
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
-train_steps 200000 \
-max_generator_batches 2 \
-dropout 0.1 \
-batch_size 4096 \
-batch_type tokens \
-normalization tokens \
-accum_count 2 \
-optim adam \
-adam_beta2 0.998 \
-decay_method noam \
-warmup_steps 8000 \
-learning_rate 2 \
-max_grad_norm 0 \
-param_init 0 \
-param_init_glorot \
-label_smoothing 0.1 \
-valid_steps 10000 \
-save_checkpoint_steps 5000 \
-world_size 8 \
-gpu_ranks 0 1 2 3 4 5 6 7"

echo "Step 3: Translate Dev"
model=$OUT/models/zh2en_step_140000.pt
python $ONMT/translate.py -model $model \
    -src $OUT/data/valid.src \
    -output $OUT/test/valid.out \
    -replace_unk -verbose -gpu 0 > $OUT/test/valid.log


echo "BPE decoding/detokenising target to match with references"
mv $OUT/test/valid.out{,.bpe} 
cat $OUT/test/valid.out.bpe | sed -E 's/(@@ )|(@@ ?$)//g' > $OUT/test/valid.out


echo "Step 4: Evaluate Dev"
$ONMT/tools/multi-bleu-detok.perl $OUT/data/valid.tgt < $OUT/test/valid.out > $OUT/test/valid.tc.bleu
$ONMT/tools/multi-bleu-detok.perl -lc $OUT/data/valid.tgt < $OUT/test/valid.out > $OUT/test/valid.lc.bleu

#===== EXPERIMENT END ======