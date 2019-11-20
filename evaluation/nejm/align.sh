bleualign=~/projects/Bleualign/bleualign.py
moore=~/software/bilingual-sentence-aligner/
data=/mnt/scratch/boxiang/projects/med_translation/processed_data/evaluation/nejm/translation/

# Bleualign
for doc in `ls $data/doc*_zh.snt`; do
	$bleualign --factored \
	-s $doc \
	-t ${doc/_zh/_en} \
	--srctotarget ${doc/.snt/.2en} \
	--printempty --verbosity 2 \
	-o ${doc/_zh.snt/.ba}
done 
cat $data/doc*.ba-s > $data/align.ba-s
cat $data/doc*.ba-t > $data/align.ba-t
rm $data/doc*.ba-{s,t}


# Bleualign (both directions):
for doc in `ls $data/doc*_zh.snt`; do
	$bleualign --factored \
	-s $doc \
	-t ${doc/_zh/_en} \
	--srctotarget ${doc/.snt/.2en} \
	--targettosrc ${doc/_zh.snt/_en.2zh} \
	--printempty --verbosity 2 \
	-o ${doc/_zh.snt/.ba2}
done 
cat $data/doc*.ba2-s > $data/align.ba2-s
cat $data/doc*.ba2-t > $data/align.ba2-t
rm $data/doc*.ba2-{s,t}


# Gale-Church:
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

cat $data/doc*.gc-s > $data/align.gc-s
cat $data/doc*.gc-t > $data/align.gc-t
rm $data/doc*.gc-{s,t}

# Moore's algorithm (IBM 1):

# Adding parallel corpora for IBM 1 model construction.
head -n 100000 /mnt/data/boxiang/wmt18/train/corpus.zh > \
$data/wmt18_zh.snt
head -n 100000 /mnt/data/boxiang/wmt18/train/corpus.en > \
$data/wmt18_en.snt

# Moore's algorithm is modified to allow factored sentences. 
# One can factor sentences by the pipe "|" character. Only the 
# first factor will be used in alignment
cd $moore # Must run in this directory
perl $moore/align-sents-all-multi-file.pl \
$data/ 0.5
cat $data/doc*_zh.snt.aligned > $data/align.moore-s
cat $data/doc*_en.snt.aligned > $data/align.moore-t