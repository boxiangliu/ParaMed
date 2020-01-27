moore=~/software/bilingual-sentence-aligner/
data=/mnt/scratch/boxiang/projects/med_translation/processed_data/evaluation/nejm/translation/
out_dir=../processed_data/evaluation/nejm/align/
[[ -f $out_dir ]] && mkdir -p $out_dir

# Moore's algorithm (IBM 1):

# Adding parallel corpora for IBM 1 model construction.
mkdir -p $data/tmp/
head -n 100000 /mnt/data/boxiang/wmt18/train/corpus.zh > \
$data/tmp/wmt18_zh.snt
head -n 100000 /mnt/data/boxiang/wmt18/train/corpus.en > \
$data/tmp/wmt18_en.snt
ln $data/doc* $data/tmp/

# Moore's algorithm is modified to allow factored sentences. 
# One can factor sentences by the pipe "|" character. Only the 
# first factor will be used in alignment
mkdir -p $out_dir/moore/
cd $moore # Must run in this directory
perl $moore/align-sents-all-multi-file.pl \
$data/tmp 0.5
cat $data/tmp/doc*_zh.snt.aligned > $out_dir/moore/align.moore-s
cat $data/tmp/doc*_en.snt.aligned > $out_dir/moore/align.moore-t
# rm $data/tmp/