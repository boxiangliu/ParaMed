bleualign=~/projects/Bleualign/bleualign.py
moore=~/software/bilingual-sentence-aligner/
data=/mnt/scratch/boxiang/projects/med_translation/data/wmt19_biomed_modified/

# Bleualign
for doc in `awk '{print $1}' $data/medline_zh2en_zh.txt | uniq`; do
	$bleualign --factored \
	-s $data/separate_docs/${doc}_zh.snt \
	-t $data/separate_docs/${doc}_en.snt \
	--srctotarget $data/separate_docs/${doc}_zh.2en \
	--printempty --verbosity 2 \
	-o $data/$doc.ba
done 
cat $data/separate_docs/doc*.ba-s > $data/align.tok.mark.ba-s
cat $data/separate_docs/doc*.ba-t > $data/align.tok.mark.ba-t
rm $data/separate_docs/doc*.ba-{s,t}

# Gale-Church:
for doc in `awk '{print $1}' $data/medline_zh2en_zh.txt | uniq`; do
	$bleualign --factored \
	-s $data/separate_docs/${doc}_zh.snt \
	-t $data/separate_docs/${doc}_en.snt \
	--srctotarget - \
	--galechurch \
	--printempty \
	--verbosity 2 \
	-o $data/$doc.gc
done 

cat $data/separate_docs/doc*.gc-s > $data/align.tok.mark.gc-s
cat $data/separate_docs/doc*.gc-t > $data/align.tok.mark.gc-t
rm $data/separate_docs/doc*.gc-{s,t}

# Moore's algorithm (IBM 1):

# Adding parallel corpora for IBM 1 model construction.
head -n 100000 /mnt/data/boxiang/wmt18/train/corpus.zh > \
$data/separate_docs/wmt18_zh.snt
head -n 100000 /mnt/data/boxiang/wmt18/train/corpus.en > \
$data/separate_docs/wmt18_en.snt

# Moore's algorithm is modified to allow factored sentences. 
# One can factor sentences by the pipe "|" character. Only the 
# first factor will be used in alignment
cd $moore # Must run in this directory
perl $moore/align-sents-all-multi-file.pl \
$data/separate_docs/ 0.5
cat $data/separate_docs/doc*_zh.snt.aligned > $data/align.tok.mark.moore-s
cat $data/separate_docs/doc*_en.snt.aligned > $data/align.tok.mark.moore-t