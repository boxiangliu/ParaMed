onmt=~/projects/OpenNMT-py/onmt/
data=~/projects/OpenNMT-py/data/

$onmt/bin/preprocess.py \
-train_src $data/src-train.txt \
-train_tgt $data/tgt-train.txt \
-valid_src $data/src-val.txt \
-valid_tgt $data/tgt-val.txt \
-save_data $data/demo


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
