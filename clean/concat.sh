# Concatenate sentences from alignment by Moore

in_dir=../processed_data/alignment/moore/align/
out_dir=../processed_data/clean/concat/
mkdir -p $out_dir


echo "$(ls $in_dir/*zh | wc -l | cut -d " " -f1) articles found in $in_dir"
[[ -f $out_dir/all.align.txt ]] && rm $out_dir/all.align.txt
for zh in $in_dir/*zh; do

	echo "Article: $zh"
	doc=$(basename $zh .align.zh)

	length=$(wc -l $zh | cut -d " " -f1)
	echo "$length lines in total"

	en=${zh/.zh/.en}
	
	[[ -f /tmp/doc.txt ]] && rm /tmp/doc.txt
	[[ -f /tmp/sent.txt ]] && rm /tmp/sent.txt
	

	echo "Creating doc ID and sentence number"
	for i in `seq 1 $length`; do
		echo $doc >> /tmp/doc.txt
		echo $i >> /tmp/sent.txt
	done

	echo "Concatenating Chinese and English articles"
	paste /tmp/doc.txt /tmp/sent.txt $zh $en >> $out_dir/all.align.txt
done