bleualign=~/projects/Bleualign/bleualign.py
moore=~/software/bilingual-sentence-aligner/
data=../data/wmt19_biomed_modified/

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

# Moore's algorithm:
perl $moore/align-sents-all-multi-file.pl \
/mnt/scratch/boxiang/projects/med_translation/data/wmt19_biomed_modified/separate_docs/ 0.5