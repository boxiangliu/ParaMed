in_dir=../processed_data/evaluation/nejm/align/bleualign/translate/
out_dir=../processed_data/evaluation/nejm/align/bleualign/input/
mkdir -p $out_dir

for zh in $in_dir/doc*.zh; do
	en=${zh/.zh/.en}
	en_base=$(basename $en)
	zh_base=$(basename $zh)
	stem=${zh_base%.*}
	echo "Document Number: $stem"

	# Add document-sentence markers:
	awk '{print $0" | "v1","NR}' \
	v1=$stem $zh > \
	$out_dir/$zh_base.mark

	awk '{print $0" | "v1","NR}' \
	v1=$stem $zh.2en > \
	$out_dir/$zh_base.2en.mark

	awk '{print $0" | "v1","NR}' \
	v1=$stem $en > \
	$out_dir/$en_base.mark

	awk '{print $0" | "v1","NR}' \
	v1=$stem $en.2zh > \
	$out_dir/$en_base.2zh.mark
done