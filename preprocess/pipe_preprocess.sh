# Turn English sentences into lower case and normalize 
# punctuations:
bash preprocess/normalize.sh

# Split paragraphs into sentences: 
python3 preprocess/detect_sentences.py 

# Tokenize sentences: 
bash preprocess/tokenize.sh 
