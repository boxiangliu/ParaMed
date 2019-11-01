onmt=~/projects/OpenNMT-py/onmt/
data=~/projects/med_translation/data/uncorpus/

$onmt/bin/preprocess.py \
-train_src $data/en-zh/UNv1.0.en-zh.zh \
-train_tgt $data/en-zh/UNv1.0.en-zh.en \
-valid_src $data/testsets/devset/UNv1.0.devset.zh \
-valid_tgt $data/testsets/devset/UNv1.0.devset.en \
-save_data $data/en-zh/UNv1.0.en-zh


$onmt/bin/train.py \
-data $data/demo \
-save_model $onmt/demo/demo-model \
-world_size 8 \
-gpu_ranks 0 1 2 3 4 5 6 7 \
--train_from $onmt/demo/demo-model/demo-model_step_25000.pt

$onmt/bin/translate.py \
-model $onmt/demo/demo-model_step_100000.pt \
-src $data/src-test.txt \
-output pred.txt \
-replace_unk -verbose
