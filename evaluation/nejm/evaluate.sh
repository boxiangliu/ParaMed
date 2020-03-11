# This will calculate the precision and recall for the following algoriths:
# ba: Bleualign
# ba2: Bleualign with bidirectional translation
# gc: Gale-Church
# moore: Moore's IBM 1 model.

in_dir=../processed_data/evaluation/nejm/align/
out_dir=../processed_data/evaluation/nejm/evaluate/
mkdir -p $out_dir

declare -A container=( [moore]=moore/align/ \
	[hunalign]=hunalign/align/ [gale_church]=bleualign/align/gale_church/ \
	[bleualign1]=bleualign/align/one_sided/ [bleualign2]=bleualign/align/two_sided/ )

for algo in ${!container[@]}; do
	echo Algorithm: $algo
	dir=${container[$algo]}
	for wd in $in_dir/$dir/*/; do
		threshold=$(basename $wd)
		echo $threshold

		# This will generate src <=> tgt alignment. 
		python3 evaluation/nejm/gen_align_file.py \
		--src_fn $wd/align.zh \
		--tgt_fn $wd/align.en \
		--out_fn $out_dir/${algo}_${threshold}.align


		# Evaluate algorithm:
		python3 evaluation/nejm/evaluate.py \
		--align_fn ../processed_data/preprocess/manual_align/alignment/align.txt \
		--pred_fn $out_dir/${algo}_${threshold}.align \
		--out_fn $out_dir/${algo}_${threshold}.pr


	done
done