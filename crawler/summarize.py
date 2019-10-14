import os
import re
import sys
sys.path.append("/Users/boxiang/Documents/work/Baidu/"\
	"projects/mosesdecoder/scripts/tokenizer/")
import mosestokenizer
import pandas as pd
from collections import defaultdict
from nltk.tokenize import word_tokenize


from utils.utils import Container, get_article_as_lowercase_string, \
	get_nltk_sent_tokenizer, RegexSentenceTokenizer


url_dir = "../processed_data/crawler/nejm/urls/"

class Article():
	def __init__(self, path, sent_tokenizers, lan):
		self.path = path
		self.lan = lan
		self.article = get_article_as_lowercase_string(path)
		self.paragraphs = self.article.split("\n")
		self.sent_tokenizers = sent_tokenizers \
			if isinstance(sent_tokenizers, list) \
			else [sent_tokenizers] 
		self.sentences = self.get_sentences(
			self.sent_tokenizers, self.paragraphs)
		self.words = word_tokenize(self.article)

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


container = Container()
container.read_from_disk(url_dir)

nltk_sent_tokenizer = get_nltk_sent_tokenizer(container, lan="en")
regex_sent_tokenizer = RegexSentenceTokenizer(regex="\.[0-9]{1,3}[,-]{1}[0-9]{1,3}|\.[0-9]{1,3}")

path = "../processed_data/crawler/nejm/articles/2019/01月/• 急性感染和心肌梗死.en"
path = "test.en"
article = Article(path=path, sent_tokenizers=[nltk_sent_tokenizer, regex_sent_tokenizer],lan="en")
article = get_article_as_lowercase_string(path)
normalize = mosestokenizer.punctnormalizer.MosesPunctuationNormalizer(lang="en")
normalize("«Hello World» — she said…")
outputfile = sys.stdout
with outputfile:
	for line in article.split("\n"):
		print(normalize(line), file=outputfile)
