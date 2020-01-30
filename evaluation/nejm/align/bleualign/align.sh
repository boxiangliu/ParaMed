bleualign=~/projects/Bleualign/bleualign.py
data=/mnt/scratch/boxiang/projects/med_translation/processed_data/evaluation/nejm/align/bleualign/input/
out_dir=/mnt/scratch/boxiang/projects/med_translation/processed_data/evaluation/nejm/align/bleualign/align/
mkdir -p $out_dir

# Bleualign
for threshold in `seq 0 5 100`; do
	mkdir -p $out_dir/one_sided/$threshold/
	for doc in `ls $data/doc*.zh.mark`; do
		$bleualign --factored \
		-s $doc \
		-t ${doc/.zh./.en.} \
		--srctotarget ${doc/.zh./.zh.2en.} \
		--filter sentences \
		--filterthreshold $threshold \
		--filterlang \
		--verbosity 1 \
		-o ${doc/.zh.mark/.align}
	done 

	mv $data/*align-{s,t} $out_dir/one_sided/$threshold/
	cat $out_dir/one_sided/$threshold/doc*.align-s > \
		$out_dir/one_sided/$threshold/align.zh
	cat $out_dir/one_sided/$threshold/doc*.align-t > \
		$out_dir/one_sided/$threshold/align.en
done
# cat $data/doc*.ba-s > $out_dir/ba/align.ba-s
# cat $data/doc*.ba-t > $out_dir/ba/align.ba-t
# rm $data/doc*.ba-{s,t}

# Bleualign (both directions):
for threshold in `seq 0 5 100`; do
	mkdir -p $out_dir/two_sided/$threshold/
	for doc in `ls $data/doc*.zh.mark`; do
		$bleualign --factored \
		-s $doc \
		-t ${doc/.zh/.en} \
		--srctotarget ${doc/.zh./.zh.2en.} \
		--targettosrc ${doc/.zh./.en.2zh.} \
		--filter sentences \
		--filterthreshold $threshold \
		--filterlang \
		--verbosity 1 \
		-o ${doc/.zh.mark/.align}
	done 

	mv $data/*align-{s,t} $out_dir/two_sided/$threshold/
	cat $out_dir/two_sided/$threshold/doc*.align-s > \
		$out_dir/two_sided/$threshold/align.zh
	cat $out_dir/two_sided/$threshold/doc*.align-t > \
		$out_dir/two_sided/$threshold/align.en
done



# Gale-Church:
for threshold in `seq 0 5 100`; do
	mkdir -p $out_dir/gale_church/$threshold/
	for doc in `ls $data/doc*.zh.mark`; do
		$bleualign --factored \
		-s $doc \
		-t ${doc/.zh/.en} \
		--srctotarget - \
		--galechurch \
		--filter sentences \
		--filterthreshold $threshold \
		--filterlang \
		--verbosity 1 \
		-o ${doc/.zh.mark/.align}
	done 
	mv $data/*align-{s,t} $out_dir/gale_church/$threshold/
	rm $data/*bad-{s,t}
	cat $out_dir/gale_church/$threshold/doc*.align-s > \
		$out_dir/gale_church/$threshold/align.zh
	cat $out_dir/gale_church/$threshold/doc*.align-t > \
		$out_dir/gale_church/$threshold/align.en
done