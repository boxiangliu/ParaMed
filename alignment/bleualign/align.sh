bleualign=~/projects/Bleualign/bleualign.py
trans_dir=../processed_data/alignment/bleualign/translate/
src_dir=../processed_data/preprocess/sentences/
align_dir=../processed_data/alignment/bleualign/align/

for src in `ls $src_dir/*.zh.tok`; do

	tgt=${src/.zh.tok/.en.tok}
	base=`basename $src`
	trans=$trans_dir/${base}.to_en
	align=$align_dir/${base/.zh.tok/.align}
	echo $base

	$bleualign \
	-s $src \
	-t $tgt \
	--srctotarget $trans \
	-o $align

done