# Turn English sentences into lower case and normalize 
# punctuations:
bash preprocess/normalize.sh

# Split paragraphs into sentences: 
python3 preprocess/detect_sentences.py 

# Tokenize sentences: 
bash preprocess/tokenize.sh 

/mnt/home/boxiang/software/anaconda2/envs/py3/bin/python preprocess/translation.py \
--article_path_list ../processed_data/crawler/nejm/translation/input_list \
--out_dir ../processed_data/crawler/nejm/translation/