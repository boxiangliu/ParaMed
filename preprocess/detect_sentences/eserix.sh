# Must run on asimovbld-1
eserix=/Users/boxiang/Documents/tools/eserix/build/bin/eserix
in_dir=../processed_data/preprocess/normalize/
out_dir=../processed_data/preprocess/sentences/eserix/
rule_fn=/Users/boxiang/Documents/tools/eserix/srx/rules.srx
mkdir -p $out_dir

for lang in en zh; do

	for article in `ls $in_dir/*.filt.$lang`; do

		echo $article

		base=$(basename $article)
		out_fn=$out_dir/$base
		mkdir -p $out_dir/$sub_dir

		echo Language: $lang
		echo Output: $out_fn

		cat $article | \
		$eserix -t -l $lang \
		-r $rule_fn > \
		$out_fn
	done
done