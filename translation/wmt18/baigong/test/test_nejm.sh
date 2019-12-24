# detokenize 
ONMT=/mnt/home/boxiang/projects/OpenNMT-py
model_dir=/mnt/home/baigong/scratch_SMT/seqtoseq/mymodels/
model=$model_dir/zh2en/bpe/model_step_370000.pt

data_dir=../processed_data/preprocess/alignment/
src=$data_dir/nejm_valid.parallel.tok.zh
tgt=$data_dir/nejm_valid.parallel.tok.en
out_dir=../processed_data/translation/baigong/test/nejm/
mkdir -p $out_dir
translation=$out_dir/nejm_valid.parallel.tok.zh.2en

# BPE:
bpe_dict=/mnt/home/baigong/data/wmt18zh-en/org/bpe_dict
BPE_Path='/mnt/home/baigong/subword-nmt/subword_nmt'
$BPE_Path/apply_bpe.py -c $bpe_dict.zh < $src > $src.bpe

for i in 1 5 10 15; do

echo "Translate.."
python $ONMT/translate.py \
	-batch_size 1 \
	-model $model \
    -src $src.bpe \
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
