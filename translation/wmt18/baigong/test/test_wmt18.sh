# detokenize 
ONMT=/mnt/home/boxiang/projects/OpenNMT-py
model_dir=/mnt/home/baigong/scratch_SMT/seqtoseq/mymodels/
model=$model_dir/zh2en/bpe/model_step_370000.pt
data_dir=/mnt/home/baigong/data/wmt18zh-en/org/
src=$data_dir/newstest2017.tc.bpe.zh
tgt=$data_dir/newstest2017.tc.en
out_dir=../processed_data/translation/baigong/test/wmt18/
mkdir -p $out_dir
translation=$out_dir/newstest2017.tc.bpe.zh.2en

for i in 1 5 10 15; do

echo "Translate.."
python $ONMT/translate.py \
	-batch_size 1 \
	-model $model \
    -src $src \
    -output $translation.beam_size$i \
    -replace_unk -verbose \
    -beam_size $i \
    -length_penalty avg \
    -gpu 0 > $translation.beam_size$i.log

mv $translation.beam_size$i{,.bpe}
cat $translation.beam_size$i.bpe | sed -E 's/(@@ )|(@@ ?$)//g' > $translation.beam_size$i
$ONMT/tools/multi-bleu.perl -lc $tgt < $translation.beam_size$i > $out_dir/bleu.lc.beam_size$i
$ONMT/tools/multi-bleu.perl $tgt < $translation.beam_size$i > $out_dir/bleu.beam_size$i
done
