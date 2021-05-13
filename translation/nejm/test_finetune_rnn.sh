#!/bin/bash
# Must be run on GPU nodes:
ONMT=/mnt/home/boxiang/projects/OpenNMT-py
WMT18=../processed_data/translation/wmt18/train_rnn/ # Path to the WMT18 baseline model.
NEJM=../processed_data/translation/nejm/finetune_rnn/ # Path to model fine-tuned on NEJM.
BPE_DIR=../processed_data/translation/wmt18/train/data/
VALID_DATA=../processed_data/split_data/split_train_test/ # Path to NEJM valid set.


TEST_SRC=$VALID_DATA/nejm.test.zh
TEST_TGT=$VALID_DATA/nejm.test.en
$ONMT/tools/apply_bpe.py -c $BPE_DIR/bpe-codes.zh < $TEST_SRC > $NEJM/test/test.zh
$ONMT/tools/apply_bpe.py -c $BPE_DIR/bpe-codes.en < $TEST_TGT > $NEJM/test/test.en

src=$NEJM/test/test.zh
tgt=$NEJM/test/test.en

# Testing Chinese to English translation:
models=($WMT18/models/zh2en_step_500000.pt  \
    $NEJM/models/4000/zh2en_step_510000.pt \
    $NEJM/models/8000/zh2en_step_510000.pt \
    $NEJM/models/16000/zh2en_step_510000.pt \
    $NEJM/models/32000/zh2en_step_510000.pt \
    $NEJM/models/64000/zh2en_step_510000.pt \
    $NEJM/models/93303/zh2en_step_510000.pt)

translations=(wmt18.zh2en \
    nejm.4000.zh2en \
    nejm.8000.zh2en \
    nejm.16000.zh2en \
    nejm.32000.zh2en \
    nejm.64000.zh2en \
    nejm.93303.zh2en)

for i in {0..6}; do
    model=${models[$i]}
    translation=${translations[$i]}

    echo "Translate $translation"
    python $ONMT/translate.py \
        -batch_size 1 \
        -model $model \
        -src $src \
        -output $NEJM/test/$translation \
        -replace_unk -verbose \
        -beam_size 1 \
        -gpu 0 > $NEJM/test/${translation}.log


    echo "BPE decoding/detokenising target to match with references"
    mv $NEJM/test/$translation{,.bpe}
    cat $NEJM/test/$translation.bpe | sed -E 's/(@@ )|(@@ ?$)//g' > $NEJM/test/$translation
    echo $NEJM/test/$translation

    $ONMT/tools/multi-bleu.perl $TEST_TGT < $NEJM/test/$translation > $NEJM/test/$translation.tc.bleu

done

# Testing English to Chinese translation:
models=($WMT18/models/en2zh_step_485000.pt  \
    $NEJM/models/4000/en2zh_step_495000.pt \
    $NEJM/models/8000/en2zh_step_495000.pt \
    $NEJM/models/16000/en2zh_step_495000.pt \
    $NEJM/models/32000/en2zh_step_495000.pt \
    $NEJM/models/64000/en2zh_step_495000.pt \
    $NEJM/models/93303/en2zh_step_495000.pt)

translations=(wmt18.en2zh \
    nejm.4000.en2zh \
    nejm.8000.en2zh \
    nejm.16000.en2zh \
    nejm.32000.en2zh \
    nejm.64000.en2zh \
    nejm.93303.en2zh)

for i in {0..6}; do
    model=${models[$i]}
    translation=${translations[$i]}

    echo "Translate $translation"
    python $ONMT/translate.py \
        -batch_size 1 \
        -model $model \
        -src $tgt \
        -output $NEJM/test/$translation \
        -replace_unk -verbose \
        -beam_size 1 \
        -gpu 0 > $NEJM/test/${translation}.log

    echo "BPE decoding/detokenising target to match with references"
    mv $NEJM/test/$translation{,.bpe}
    cat $NEJM/test/$translation.bpe | sed -E 's/(@@ )|(@@ ?$)//g' > $NEJM/test/$translation
    echo $NEJM/test/$translation

    $ONMT/tools/multi-bleu.perl $TEST_SRC < $NEJM/test/$translation > $NEJM/test/$translation.tc.bleu

done
