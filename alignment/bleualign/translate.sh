export onmt=~/projects/OpenNMT-py/onmt/
export data=/mnt/data/boxiang/wmt18/
export model=../processed_data/translation/wmt18/
export src_dir=../processed_data/preprocess/sentences/
export out_dir=../processed_data/alignment/bleualign/translate/

translate(){
	src=$1
	gpu=$(($2 % 10))

	echo "Source file:" $src
	echo "GPU:" $gpu

	$onmt/bin/translate.py \
	-model $model/zh-en_2_step_120000.pt \
	-src $src \
	-output $out_dir/`basename $src`.to_en \
	-replace_unk \
	-gpu $gpu	
}

export -f translate
parallel --jobs 10 translate {1} {2} ::: `ls $src_dir/*.zh.tok` :::+ {1..2049}
