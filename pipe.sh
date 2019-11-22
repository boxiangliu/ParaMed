# Crawl NEJM websites:
python3 crawler/crawl.py 


#################
# Preprocessing #
#################
# Preprocess NEJM articles
# Step 1:
# Turn English sentences into lower case and normalize 
# punctuations, also remove :
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
bash translation/wmt18/train.sh

##############
# Evaluation #
##############

#---- Abstracts -----#

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

# Evaluate precision and recall for different algorithms:
bash evaluation/wmt19_biomed/evaluate.sh


#------ NEJM articles -------#
# Manually aligned gold-standard for NEJM articles:
# Don't run.
bash preprocess/manual_align.sh

# This will do necessary preprocessing (segmentation, tokenization, BPE)
# and generate sentence-to-sentence translation. Additionally, it will
# also mark each sentence with doc#,# markers.
# Must be run with GPUs. 
bash evaluation/nejm/translate.sh

# Here I align with Bleualign, Gale-Church, and Moore's IBM 1 model.
bash evaluation/nejm/align.sh

# Evaluate precision and recall for different algorithms:
bash evaluation/nejm/evaluate.sh


#############
# Alignment #
#############
# Use Moore's algorithm to align and create training set:
bash alignment/moore/align.sh

# Create validation set:
python3 utils/gen_para_corp.py \
	--align_fn ../processed_data/preprocess/alignment/align_validation_zh_en.txt \
	--zh_fn ../processed_data/preprocess/alignment/nejm_valid.zh \
	--en_fn ../processed_data/preprocess/alignment/nejm_valid.en \
	--out_fn ../processed_data/preprocess/alignment/nejm_valid.parallel


###############
# Translation #
###############
# Testing the WMT18 model on NEJM journal:
python3 translation/wmt18/test.sh


# Fine-tune on NEJM dataset:
python3 translation/nejm/train.sh


# Test on NEJM dataset:
python3 translation/nejm/test.sh