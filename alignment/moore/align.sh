moore=~/software/bilingual-sentence-aligner/
data=/mnt/scratch/boxiang/projects/med_translation/processed_data/preprocess/sentences/
out_dir=/mnt/scratch/boxiang/projects/med_translation/processed_data/alignment/moore/align/
[[ ! -f $out_dir ]] && mkdir -p $out_dir


if [[ -f $out_dir/mapdocs_zh_en.txt ]]; then
	rm $out_dir/mapdocs_zh_en.txt
fi

n=0
for article in `ls $data/*.zh.tok`; do
	n=$(($n+1))
	base=`basename $article`
	base=${base/.zh.tok/}
	echo -e "doc${n}\t$base" >> $out_dir/mapdocs_zh_en.txt
done


# These validation files needs to be removed from the training set.
valid_art=(鼻咽癌的吉西他滨联合顺铂诱导化疗 \
	饮水可对饮用含糖饮料产生多大程度的对抗作用 \
	帕妥珠单抗和曲妥珠单抗辅助治疗早期HER2阳性乳腺癌)

art_no=()
for art in ${valid_art[@]}; do
	art_no+=(`grep $art $out_dir/mapdocs_zh_en.txt | awk '{print $1}'`)
done

n=0
for article in `ls $data/*.zh.tok`; do
	n=$(($n+1))
	prefix=${article/.zh.tok/}

	# Exclude validation files:
	if [[ ${art_no[@]} =~ (^|[[:space:]])"doc$n"($|[[:space:]]) ]]; then
		echo "doc$n is in valid set; skipping..."
		continue
	fi

	base=`basename $prefix`
	en_art=$out_dir/doc${n}_en.snt
	zh_art=$out_dir/doc${n}_zh.snt

	zh_lines=`wc -l ${prefix}.zh.tok | cut -d" " -f1`
	en_lines=`wc -l ${prefix}.en.tok | cut -d" " -f1`
	if [[ $zh_lines -gt 0 && $en_lines -gt 0 ]]; then
		awk '{print $0" | doc"v1","NR}' \
		v1=$n ${prefix}.zh.tok > \
		$zh_art

		awk '{print $0" | doc"v1","NR}' \
		v1=$n ${prefix}.en.tok > \
		$en_art
	else
		echo "$prefix has 0 lines."
	fi
done

# Adding parallel corpora for IBM 1 model construction.
head -n 100000 /mnt/data/boxiang/wmt18/train/corpus.zh > \
$out_dir/wmt18_zh.snt
head -n 100000 /mnt/data/boxiang/wmt18/train/corpus.en > \
$out_dir/wmt18_en.snt


# Align with Moore's algorithm:
cd $moore # Must run in this directory
perl $moore/align-sents-all-multi-file.pl \
$out_dir/ 0.5
cat $out_dir/doc*_zh.snt.aligned > $out_dir/nejm.zh
cat $out_dir/doc*_en.snt.aligned > $out_dir/nejm.en


# Generate alignment file
cd $med_translation/scripts
python3 evaluation/wmt19_biomed/gen_align_file.py \
	--src_fn $out_dir/nejm.zh \
	--tgt_fn $out_dir/nejm.en \
	--out_fn $out_dir/nejm.align

# Remove line markers:
sed -i -E "s/ \| doc[0-9]+,[0-9]+//g" $out_dir/nejm.zh
sed -i -E "s/ \| doc[0-9]+,[0-9]+//g" $out_dir/nejm.en

# Remove intermediate files:
mkdir $out_dir/intermediate/
mv $out_dir/*.words $out_dir/intermediate/
mv $out_dir/*.aligned $out_dir/intermediate/
mv $out_dir/*.snt $out_dir/intermediate/
mv $out_dir/*.search-nodes $out_dir/intermediate/
mv $out_dir/*.length-backtrace $out_dir/intermediate/
mv $out_dir/*.backtrace $out_dir/intermediate/
mv $out_dir/*.train $out_dir/intermediate/
mv $out_dir/{model-one,sentence-file-pair-list} $out_dir/intermediate/