hunalign=/mnt/home/boxiang/software/hunalign-1.1/src/hunalign/hunalign
ladder2text=/mnt/home/boxiang/software/hunalign-1.1/scripts/ladder2text.py
dictionary=/mnt/home/boxiang/software/hunalign-1.1/data/null.dic
original_dir=../processed_data/sentence_alignment/split/
tokenized_dir=../processed_data/sentence_alignment/tokenize/
out_dir=../processed_data/sentence_alignment/alignment/
mkdir -p $out_dir

[[ -f $out_dir/batch ]] && rm $out_dir/batch

for a in $(ls $tokenized_dir/*/en_*.nobreak.txt); do
	src=$a
	tgt=${a/en_/sp_}
	out=${a/$tokenized_dir/$out_dir}
	out=${out/.txt/.ladder}
	[[ ! -f $(dirname $out) ]] && mkdir -p $(dirname $out)
	echo -e "$src\t$tgt\t$out" >> $out_dir/batch
done

$hunalign -batch $dictionary $out_dir/batch

while read line; do
	src=$(echo "$line" | cut -f1)
	tgt=$(echo "$line" | cut -f2)
	ladder=$(echo "$line" | cut -f3)
	
	echo "Tokenized bitext"
	echo Source: $src 
	echo Target: $tgt
	echo Alignment: $ladder
	
	bitext=${ladder/.ladder/.tok.bitext}
	python2.7 $ladder2text $ladder $src $tgt > $bitext

	echo "Original bitext"
	src=${src/$tokenized_dir/$original_dir}
	tgt=${tgt/$tokenized_dir/$original_dir}

	echo Source: $src 
	echo Target: $tgt
	echo Alignment: $ladder

	bitext=${ladder/.ladder/.bitext}
	python2.7 $ladder2text $ladder $src $tgt > $bitext

done < $out_dir/batch..