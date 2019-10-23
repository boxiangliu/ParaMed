import os
import re
import sys
import glob

import pandas as pd
from utils.utils import Container, get_article_as_lowercase_string, \
	get_nltk_sent_tokenizer, RegexSentenceTokenizer

article_dir = "/Users/boxiang/Documents/work/Baidu/projects/"\
	"med_translation/processed_data/crawler/nejm/articles_norm/"
sentence_dir = "/Users/boxiang/Documents/work/Baidu/projects/"\
	"med_translation/processed_data/crawler/nejm/sentences/"
if not os.path.exists(sentence_dir):
	os.makedirs(sentence_dir)

class Article():
	def __init__(self, path, sent_tokenizers, lang):
		self.path = path
		self.lang = lang
		self.article = get_article_as_lowercase_string(path)
		self.paragraphs = self.article.split("\n")
		self.sent_tokenizers = sent_tokenizers \
			if isinstance(sent_tokenizers, list) \
			else [sent_tokenizers] 
		self.sentences = self.get_sentences(
			self.sent_tokenizers, self.paragraphs)

	def get_sentences(self, sent_tokenizers, texts):
		if not isinstance(texts, list):
			texts = [texts]

		for tokenizer in sent_tokenizers:
			sentences = []
			for t in texts:
				s = tokenizer.tokenize(t)
				sentences += s
			texts = sentences
		
		return sentences

	def write_to_disk(self, out_fn, level):
		if level == "sentence":
			with open(out_fn, "w") as f:
				for sent in self.sentences:
					f.write(sent + "\n")
		elif level == "article":
			with open(out_fn, "w") as f:
				f.write(self.article)
		elif level == "paragraph":
			with open(out_fn, "w") as f:
				for para in self.paragrahs:
					f.write(para + "\n")
		else:
			raise ValueError("Unknown level: {}".format(level))

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
# Total sentences: 143966

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
# Total sentences: 147012


