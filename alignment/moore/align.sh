moore=~/software/bilingual-sentence-aligner/
data=/mnt/scratch/boxiang/projects/med_translation/processed_data/preprocess/sentences
out_dir=/mnt/scratch/boxiang/projects/med_translation/processed_data/alignment/moore/align/
mkdir -p $out_dir


if [[ -f $out_dir/mapdocs_zh_en.txt ]]; then
	rm $out_dir/mapdocs_zh_en.txt
done

n=0
for article in `ls $data/*.zh.tok`; do
	n=$(($n+1))
	base=`basename $article`
	base=${base/.zh.tok/}
	echo -e "doc${n}\t$base" >> $out_dir/mapdocs_zh_en.txt
done

n=0
for article in `ls $data/*.zh.tok`; do
	n=$(($n+1))
	prefix=${article/.zh.tok/}
	echo Article No.: $n
	echo Name: $prefix

	base=`basename $prefix`
	en_art=$out_dir/doc${n}_en.snt
	zh_art=$out_dir/doc${n}_zh.snt

	if [[ $n =~ ^(60|182|754|218|597|1219|546|870|225|1782|379|1121|2026|294|499|1665|1811|838|1897|13|488|871|1558|137|1086|473|1071|1386|1716|1300|1119|211|923|1292|1641|613|509|1704|380)$ ]]; then
		echo Pass
	else
		awk '{print $0" | doc"v1","NR}' \
		v1=$n ${prefix}.zh.tok > \
		$zh_art

		awk '{print $0" | doc"v1","NR}' \
		v1=$n ${prefix}.en.tok > \
		$en_art
	fi
done


cd $moore # Must run in this directory
perl $moore/align-sents-all-multi-file.pl \
$out_dir/ 0.5
cat $data/doc*_zh.snt.aligned > $data/align.tok.mark.moore-s
cat $data/doc*_en.snt.aligned > $data/align.tok.mark.moore-t