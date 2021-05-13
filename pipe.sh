############
# Crawling #
############
# Crawl NEJM websites:
python3 crawler/crawl.py 

# Get article type distribution:
python3 crawler/url_stat.py 

# Filter unwanted texts:
python3 crawler/filter.py

# Get length difference before and after filtering:
python3 crawler/article_stat.py

#################
# Preprocessing #
#################
# Preprocess NEJM articles
# Step 1:
# Turn English sentences into lower case and normalize 
# punctuations, also remove:
bash preprocess/normalize.sh

# Step 2:
# Split paragraphs into sentences: 
bash preprocess/detect_sentences/eserix.sh 
python3 preprocess/detect_sentences/punkt.py
python3 preprocess/detect_sentences/sent_stat.py

# Step 3:
# Tokenize sentences and change case:
bash preprocess/tokenize.sh
bash preprocess/lowercase.sh
bash preprocess/truecase.sh

# Step 4:
# Manually align:
bash preprocess/manual_align/copy.sh
bash preprocess/manual_align/align.sh


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
# Align with Moore's algorithm:
bash evaluation/nejm/align/moore/input.sh
bash evaluation/nejm/align/moore/align.sh

# Align with Hunalign: 
bash evaluation/nejm/align/hunalign/input.sh
bash evaluation/nejm/align/hunalign/align.sh

# Align with Bleualign:
bash evaluation/nejm/align/bleualign/input.sh
bash evaluation/nejm/align/bleualign/translate.sh
bash evaluation/nejm/align/bleualign/align.sh

# Evaluate precision and recall for different algorithms:
bash evaluation/nejm/evaluate.sh

# Visually compare Precision-Recall across methods:
python3 evaluation/nejm/vis_pr_curve.py


#####################
# Machine Alignment #
#####################
# Use Moore's algorithm to align:
bash alignment/moore/input.sh
bash alignment/moore/align.sh


#########################
# Crowdsource Alignment #
#########################
# Prepare articles
python3 crowdsource/prep_articles.py


############
# Clean up #
############
# Use bifixer to remove duplicate sentences:
# Don't run (need docker container)
bash clean/concat.sh
bash clean/clean.sh 


##############
# Split data #
##############
# Split data into training, dev, test:
bash split_data/split_train_test.py


###############
# Translation #
###############
# Subset the data: 
python3 subset/subset.py

# Fine-tune on NEJM dataset:
bash translation/nejm/finetune.sh
bash translation/nejm/test_finetune.sh

# Train on NEJM from scratch:
bash translation/nejm/train_denovo.sh
bash translation/nejm/test_denovo.sh

# Plot bleu score:
python3 translation/nejm/plot_bleu.py

# Do the above things for a LSTM model: 
# Fine-tune on NEJM dataset:
bash translation/nejm/finetune_rnn.sh
bash translation/nejm/test_finetune_rnn.sh

# Train on NEJM from scratch:
bash translation/nejm/train_denovo_rnn.sh
bash translation/nejm/test_denovo_rnn.sh

# Plot bleu score:
python3 translation/nejm/plot_bleu_rnn.py

#################
# Visualization #
#################

# Make table 1
python3 visulization/tables/tab1/tab1.py