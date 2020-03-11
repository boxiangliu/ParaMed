# Moore's algorithm (IBM 1):
moore=~/software/bilingual-sentence-aligner-modified/
data=/mnt/scratch/boxiang/projects/med_translation/processed_data/evaluation/nejm/align/moore/input/
out_dir=/mnt/scratch/boxiang/projects/med_translation/processed_data/evaluation/nejm/align/moore/align/
mkdir -p $out_dir

# Moore's algorithm is modified to allow factored sentences. 
# One can factor sentences by the pipe "|" character. Only the 
# first factor will be used in alignment
cd $moore # Must run in this directory
# `seq 0 0.05 0.95 `seq 0.955 0.005 0.995``
for threshold in  `seq 0.985 0.005 0.995`; do
	echo $threshold
	perl $moore/align-sents-all-multi-file.pl $data $threshold
	mkdir -p $out_dir/$threshold/
	mv $data/doc*aligned $out_dir/$threshold/
	rm $data/*{words,backtrace,nodes,train}
	rm $data/{model-one,sentence-file-pair-list}
	cat $out_dir/$threshold/doc*_zh.snt.aligned > $out_dir/$threshold/align.zh
	cat $out_dir/$threshold/doc*_en.snt.aligned > $out_dir/$threshold/align.en
done
