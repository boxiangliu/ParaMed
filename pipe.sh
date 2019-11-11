# Crawl NEJM websites:
python crawler/crawl.py 


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

# Create a manually aligned gold-standard based on 
# WMT19 Biomedical translation shared task to  
# evaluate bleualign with WMT18 baseline model:
bash evaluation/wmt19_biomed/modifications.sh 
bash evaluation/wmt19_biomed/translate.sh 

# Evaluate bleualign with WMT18 baseline model:
python3 evaluation/wmt19_biomed/evaluate.py