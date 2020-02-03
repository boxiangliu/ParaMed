moore=~/software/bilingual-sentence-aligner-modified/
in_dir=/mnt/scratch/boxiang/projects/med_translation/processed_data/alignment/moore/input/
out_dir=/mnt/scratch/boxiang/projects/med_translation/processed_data/alignment/moore/align/
mkdir -p $out_dir
# Align with Moore's algorithm:
cd $moore # Must run in this directory
perl $moore/align-sents-all-multi-file.pl $in_dir 0.5


for f in $in_dir/*snt.aligned; do
	echo $f
	basename=$(basename $f .snt.aligned)
	basename=${basename/_/.align.}
	mv $f $out_dir/$basename
done
rm $in_dir/*{words,backtrace,nodes,train}
rm $in_dir/{model-one,sentence-file-pair-list}
rm $out_dir/wmt18.align.{zh,en}
