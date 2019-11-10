onmt=~/projects/OpenNMT-py/onmt/
data=/mnt/data/boxiang/wmt18/
model=~/projects/med_translation/processed_data/translation/wmt18/

$onmt/bin/preprocess.py \
-src_seq_length 256 \
-tgt_seq_length 256 \
-train_src $data/train/corpus.zh \
-train_tgt $data/train/corpus.en \
-valid_src $data/dev/newsdev2017.tc.zh \
-valid_tgt $data/dev/newsdev2017.tc.en \
-save_data $data/train/corpus


$onmt/bin/train.py \
-data $data/train/corpus \
-save_model $model/zh-en_2 \
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
&> $model/zh-en_2.log

