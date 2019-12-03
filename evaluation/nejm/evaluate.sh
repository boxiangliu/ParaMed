# This will calculate the precision and recall for the following algoriths:
# ba: Bleualign
# ba2: Bleualign with bidirectional translation
# gc: Gale-Church
# moore: Moore's IBM 1 model.

mkdir -p ../processed_data/evaluation/nejm/evaluate/
for algo in ba ba2 gc moore; do

	# This will generate src <=> tgt alignment. 
	python3 evaluation/wmt19_biomed/gen_align_file.py \
	--src_fn ../processed_data/evaluation/nejm/align/$algo/align.${algo}-s \
	--tgt_fn ../processed_data/evaluation/nejm/align/$algo/align.${algo}-t \
	--out_fn ../processed_data/evaluation/nejm/align/$algo/align_${algo}_zh_en.txt


	# Evaluate algorithm:
	python3 evaluation/wmt19_biomed/evaluate.py \
	--align_fn ../processed_data/preprocess/alignment/align_validation_zh_en.txt \
	--pred_fn ../processed_data/evaluation/nejm/align/$algo/align_${algo}_zh_en.txt \
	--out_fn ../processed_data/evaluation/nejm/evaluate/${algo}.pr

done