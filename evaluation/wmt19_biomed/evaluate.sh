# This will calculate the precision and recall for the following algoriths:
# ba: Bleualign
# ba2: Bleualign with bidirectional translation
# gc: Gale-Church
# moore: Moore's IBM 1 model.

for algo in ba gc moore; do
	# This will generate src <=> tgt alignment. 
	python3 evaluation/wmt19_biomed/gen_align_file.py \
	--src_fn ../data/wmt19_biomed_modified/align.tok.mark.${algo}-s \
	--tgt_fn ../data/wmt19_biomed_modified/align.tok.mark.${algo}-t \
	--out_fn ../data/wmt19_biomed_modified/align_${algo}_zh_en.txt

	# Evaluate algorithm:
	python3 evaluation/wmt19_biomed/evaluate.py \
	--align_fn ../data/wmt19_biomed_modified/align_validation_zh_en.txt \
	--en_fn ../data/wmt19_biomed_modified/medline_zh2en_en.txt \
	--zh_fn ../data/wmt19_biomed_modified/medline_zh2en_zh.txt \
	--pred_fn ../data/wmt19_biomed_modified/align_${algo}_zh_en.txt \
	--out_fn ../processed_data/evaluation/wmt19_biomed/evaluate/${algo}.pr
done