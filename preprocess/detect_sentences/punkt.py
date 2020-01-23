import os
import re
import sys
import glob

import pandas as pd
sys.path.append(".")
from utils.utils import Article, get_nltk_sent_tokenizer,\
	RegexSentenceTokenizer

article_dir = "../processed_data/preprocess/normalize/"
sentence_dir = "../processed_data/preprocess/sentences/punkt/"
if not os.path.exists(sentence_dir):
	os.makedirs(sentence_dir)

def save_sentences(out_fn, article):
	ns = len(article.sentences)
	with open(out_fn, "w") as f:
		for i, sent in enumerate(article.sentences):
			f.write(sent + "\n")

# English:
article_paths=glob.glob("{}/*.filt.en".format(article_dir))
nltk_sent_tokenizer = get_nltk_sent_tokenizer(article_paths, lang="en")
regex_sent_tokenizer = RegexSentenceTokenizer(regex="[^0-9]\.[0-9]{1,2}[0-9,-]*?[ \n]")

num_sents = 0
for path in article_paths:
	print("Article: {}".format(path), flush=True)
	article = Article(path=path, 
		sent_tokenizers=[nltk_sent_tokenizer, regex_sent_tokenizer],
		lang="en")
	out_fn = "{}/{}".format(sentence_dir, \
		os.path.basename(path))
	save_sentences(out_fn, article)
	num_sents += len(article.sentences)

print("Total sentences: {}".format(num_sents))
# Total sentences: 135245

# Chinese:
article_paths=glob.glob("{}/*.filt.zh".format(article_dir))
regex_sent_tokenizer = RegexSentenceTokenizer(regex=u"[^！？。]+[！？。]?[“]*?")

num_sents = 0
for path in article_paths:
	print("Article: {}".format(path), flush=True)
	article = Article(path=path, 
		sent_tokenizers=[regex_sent_tokenizer],
		lang="zh")
	out_fn = "{}/{}".format(sentence_dir, \
		os.path.basename(path))
	save_sentences(out_fn, article)
	num_sents += len(article.sentences)
print("Total sentences: {}".format(num_sents))
# Total sentences: 135225


