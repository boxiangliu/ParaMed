moses="/Users/boxiang/Documents/work/Baidu/projects/mosesdecoder/scripts/tokenizer/"
lowercase="$moses/lowercase.perl"
normalize="$moses/normalize-punctuation.perl"

in_dir="/Users/boxiang/Documents/work/Baidu/projects/med_translation/processed_data/crawler/nejm/articles/"
out_dir="/Users/boxiang/Documents/work/Baidu/projects/med_translation/processed_data/crawler/nejm/articles_norm/"
years=$(ls $in_dir)
echo "Found the following years:"
echo $years
for y in $years; do
	echo "Year: $y" 
	months=$(ls $in_dir/$y)
	echo "Found the following months:"
	echo $months
	mkdir -p $out_dir/$y

	for m in $months; do
		echo "Month: $m"
		articles_en=$(ls $in_dir/$y/$m/*.en)
		articles_zh=$(ls $in_dir/$y/$m/*.zh)
		mkdir -p $out_dir/$y/$m

		for en in $articles_en; do
			echo "Article: $en"
			# cat $en | $lowercase | $normalize > $out_dir/$y/$m/$en
		done
	done
done 