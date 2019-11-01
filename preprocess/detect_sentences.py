import os
import re
import sys
import glob

import pandas as pd
from utils.utils import Article, get_nltk_sent_tokenizer,\
	RegexSentenceTokenizer

article_dir = "../processed_data/preprocess/articles_norm/"
sentence_dir = "../processed_data/preprocess/sentences/"
if not os.path.exists(sentence_dir):
	os.makedirs(sentence_dir)

# English:
article_paths=glob.glob("{}/*.en".format(article_dir))
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
	article.write_to_disk(out_fn, level="sentence")
	num_sents += len(article.sentences)
print("Total sentences: {}".format(num_sents))
# Total sentences: 135245

# Chinese:
article_paths=glob.glob("{}/*.zh".format(article_dir))
regex_sent_tokenizer = RegexSentenceTokenizer(regex=u"[^！？。]+[！？。]?[“]*?")

num_sents = 0
for path in article_paths:
	print("Article: {}".format(path), flush=True)
	article = Article(path=path, 
		sent_tokenizers=[regex_sent_tokenizer],
		lang="zh")
	out_fn = "{}/{}".format(sentence_dir, \
		os.path.basename(path))
	article.write_to_disk(out_fn, level="sentence")
	num_sents += len(article.sentences)
print("Total sentences: {}".format(num_sents))
# Total sentences: 135225


