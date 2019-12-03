bleualign=~/projects/Bleualign/bleualign.py
moore=~/software/bilingual-sentence-aligner/
data=/mnt/scratch/boxiang/projects/med_translation/processed_data/evaluation/nejm/translation/
out_dir=/mnt/scratch/boxiang/projects/med_translation/processed_data/evaluation/nejm/align/
[[ -f $out_dir ]] && mkdir -p $out_dir

# Bleualign
mkdir -p $out_dir/ba/
for doc in `ls $data/doc*_zh.snt`; do
	$bleualign --factored \
	-s $doc \
	-t ${doc/_zh/_en} \
	--srctotarget ${doc/.snt/.2en} \
	--printempty --verbosity 2 \
	-o ${doc/_zh.snt/.ba}
done 
cat $data/doc*.ba-s > $out_dir/ba/align.ba-s
cat $data/doc*.ba-t > $out_dir/ba/align.ba-t
rm $data/doc*.ba-{s,t}


# Bleualign (both directions):
mkdir -p $out_dir/ba2/
for doc in `ls $data/doc*_zh.snt`; do
	$bleualign --factored \
	-s $doc \
	-t ${doc/_zh/_en} \
	--srctotarget ${doc/.snt/.2en} \
	--targettosrc ${doc/_zh.snt/_en.2zh} \
	--printempty --verbosity 2 \
	-o ${doc/_zh.snt/.ba2}
done 
cat $data/doc*.ba2-s > $out_dir/ba2/align.ba2-s
cat $data/doc*.ba2-t > $out_dir/ba2/align.ba2-t
rm $data/doc*.ba2-{s,t}


# Gale-Church:
mkdir -p $out_dir/gc/
for doc in `ls $data/doc*_zh.snt`; do
	$bleualign --factored \
	-s $doc \
	-t ${doc/_zh/_en} \
	--srctotarget - \
	--galechurch \
	--printempty \
	--verbosity 2 \
	-o ${doc/_zh.snt/.gc}
done 

cat $data/doc*.gc-s > $out_dir/gc/align.gc-s
cat $data/doc*.gc-t > $out_dir/gc/align.gc-t
rm $data/doc*.gc-{s,t}

# Moore's algorithm (IBM 1):

# Adding parallel corpora for IBM 1 model construction.
mkdir -p $data/tmp/
head -n 100000 /mnt/data/boxiang/wmt18/train/corpus.zh > \
$data/tmp/wmt18_zh.snt
head -n 100000 /mnt/data/boxiang/wmt18/train/corpus.en > \
$data/tmp/wmt18_en.snt
ln $data/doc* $data/tmp/

# Moore's algorithm is modified to allow factored sentences. 
# One can factor sentences by the pipe "|" character. Only the 
# first factor will be used in alignment
mkdir -p $out_dir/moore/
cd $moore # Must run in this directory
perl $moore/align-sents-all-multi-file.pl \
$data/tmp 0.5
cat $data/tmp/doc*_zh.snt.aligned > $out_dir/moore/align.moore-s
cat $data/tmp/doc*_en.snt.aligned > $out_dir/moore/align.moore-t
# rm $data/tmp/