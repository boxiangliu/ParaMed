# Crawl NEJM websites:
python3 crawler/crawl.py 


#################
# Preprocessing #
#################
# Preprocess NEJM articles
# Step 1:
# Turn English sentences into lower case and normalize 
# punctuations:
bash preprocess/normalize.sh

# Step 2:
# Split paragraphs into sentences: 
python3 preprocess/detect_sentences.py 

# Step 3:
# Tokenize sentences: 
bash preprocess/tokenize.sh 


##################
# WMT18 baseline #
##################
# Build a WMT18 baseline model. 
# Data: WMT18 news translation shared task
# Model: default transformer

# Train zh -> en on WMT18 BPE data:
# Do not run (only run on GPU nodes)
bash translation/wmt18/train_bpe.sh

##############
# Evaluation #
##############

## Abstracts ##
## Bleualign ##

# Create a manually aligned gold-standard based on 
# WMT19 Biomedical translation shared task to  
# evaluate bleualign with WMT18 baseline model:
bash evaluation/wmt19_biomed/modifications.sh 

# This will do necessary preprocessing (segmentation, tokenization, BPE)
# and generate sentence-to-sentence translation. Additionally, it will
# also mark each sentence with doc#,# markers.
bash evaluation/wmt19_biomed/translate.sh

# Here I align with Bleualign, Gale-Church, and Moore's IBM 1 model.
bash evaluation/wmt19_biomed/align.sh

# This will generate src <=> tgt alignment. 
python3 evaluation/wmt19_biomed/gen_align_file.py \
	--src_fn ../data/wmt19_biomed_modified/align.tok.mark.ba-s \
	--tgt_fn ../data/wmt19_biomed_modified/align.tok.mark.ba-t \
	--out_fn ../data/wmt19_biomed_modified/align_bleualign_zh_en.txt

# Evaluate bleualign with WMT18 baseline model:
python3 evaluation/wmt19_biomed/evaluate.py \
	--align_fn ../data/wmt19_biomed_modified/align_validation_zh_en.txt \
	--en_fn ../data/wmt19_biomed_modified/medline_zh2en_en.txt \
	--zh_fn ../data/wmt19_biomed_modified/medline_zh2en_zh.txt \
	--pred_fn ../data/wmt19_biomed_modified/align_bleualign_zh_en.txt \
	--out_fn ../processed_data/evaluation/wmt19_biomed/evaluate/bleualign.pr


## Gale-Church ##
# Align with Gale-Church algorithm:
python3 evaluation/wmt19_biomed/gen_align_file.py \
	--src_fn ../data/wmt19_biomed_modified/align.tok.mark.gc-s \
	--tgt_fn ../data/wmt19_biomed_modified/align.tok.mark.gc-t \
	--out_fn ../data/wmt19_biomed_modified/align_galechurch_zh_en.txt


# Evaluate Gale-Church results:
python3 evaluation/wmt19_biomed/evaluate.py \
	--align_fn ../data/wmt19_biomed_modified/align_validation_zh_en.txt \
	--en_fn ../data/wmt19_biomed_modified/medline_zh2en_en.txt \
	--zh_fn ../data/wmt19_biomed_modified/medline_zh2en_zh.txt \
	--pred_fn ../data/wmt19_biomed_modified/align_galechurch_zh_en.txt \
	--out_fn ../processed_data/evaluation/wmt19_biomed/evaluate/galechurch.pr


## Moore's (IBM 1) ##
python3 evaluation/wmt19_biomed/gen_align_file.py \
	--src_fn ../data/wmt19_biomed_modified/align.tok.mark.moore-s \
	--tgt_fn ../data/wmt19_biomed_modified/align.tok.mark.moore-t \
	--out_fn ../data/wmt19_biomed_modified/align_moore_zh_en.txt

python3 evaluation/wmt19_biomed/evaluate.py \
	--align_fn ../data/wmt19_biomed_modified/align_validation_zh_en.txt \
	--en_fn ../data/wmt19_biomed_modified/medline_zh2en_en.txt \
	--zh_fn ../data/wmt19_biomed_modified/medline_zh2en_zh.txt \
	--pred_fn ../data/wmt19_biomed_modified/align_moore_zh_en.txt \
	--out_fn ../processed_data/evaluation/wmt19_biomed/evaluate/moore.pr


## NEJM articles ##
# Manually aligned gold-standard for NEJM articles:
# Don't run.
bash preprocess/manual_align.sh

# This will do necessary preprocessing (segmentation, tokenization, BPE)
# and generate sentence-to-sentence translation. Additionally, it will
# also mark each sentence with doc#,# markers.
bash evaluation/nejm/translate.sh

# Here I align with Bleualign, Gale-Church, and Moore's IBM 1 model.
bash evaluation/nejm/align.sh

# This will generate src <=> tgt alignment. 
python3 evaluation/wmt19_biomed/gen_align_file.py \
	--src_fn ../processed_data/evaluation/nejm/translation/align.tok.mark.ba-s \
	--tgt_fn ../processed_data/evaluation/nejm/translation/align.tok.mark.ba-t \
	--out_fn ../processed_data/evaluation/nejm/translation/align_bleualign_zh_en.txt


# Evaluate bleualign with WMT18 baseline model:
python3 evaluation/wmt19_biomed/evaluate.py \
	--align_fn ../processed_data/preprocess/alignment/align_validation_zh_en.txt \
	--pred_fn ../processed_data/evaluation/nejm/translation/align_bleualign_zh_en.txt \
	--out_fn ../processed_data/evaluation/nejm/translation/evaluate/bleualign.pr


## Gale-Church ##
# This will generate src <=> tgt alignment. 
python3 evaluation/wmt19_biomed/gen_align_file.py \
	--src_fn ../processed_data/evaluation/nejm/translation/align.tok.mark.gc-s \
	--tgt_fn ../processed_data/evaluation/nejm/translation/align.tok.mark.gc-t \
	--out_fn ../processed_data/evaluation/nejm/translation/align_galechurch_zh_en.txt


# Evaluate Gale-Church algorithm:
python3 evaluation/wmt19_biomed/evaluate.py \
	--align_fn ../processed_data/preprocess/alignment/align_validation_zh_en.txt \
	--pred_fn ../processed_data/evaluation/nejm/translation/align_galechurch_zh_en.txt \
	--out_fn ../processed_data/evaluation/nejm/translation/evaluate/galechurch.pr


## Moore's (IBM 1) ##
python3 evaluation/wmt19_biomed/gen_align_file.py \
	--src_fn ../processed_data/evaluation/nejm/translation/align.tok.mark.moore-s \
	--tgt_fn ../processed_data/evaluation/nejm/translation/align.tok.mark.moore-t \
	--out_fn ../processed_data/evaluation/nejm/translation/align_moore_zh_en.txt

# Evaluate Moore's algorithm:
python3 evaluation/wmt19_biomed/evaluate.py \
	--align_fn ../processed_data/preprocess/alignment/align_validation_zh_en.txt \
	--pred_fn ../processed_data/evaluation/nejm/translation/align_moore_zh_en.txt \
	--out_fn ../processed_data/evaluation/nejm/translation/evaluate/moore.pr
