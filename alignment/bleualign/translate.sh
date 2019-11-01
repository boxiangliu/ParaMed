onmt=~/projects/OpenNMT-py/onmt/
data=/mnt/data/boxiang/wmt18/
model=~/projects/med_translation/processed_data/translation/wmt18/

$onmt/bin/translate.py \
-model $model/zh-en_2_step_120000.pt \
-src ../processed_data/preprocess/sentences/鼻咽癌的吉西他滨联合顺铂诱导化疗.zh.tok \
-output ../processed_data/alignment/bleualign/translate/鼻咽癌的吉西他滨联合顺铂诱导化疗.zh.to_en \
-replace_unk -verbose \
-gpu 0