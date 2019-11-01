import os
import re
import sys
import glob

import pandas as pd
import matplotlib.pyplot as plt

from collections import Counter
from utils.utils import Container, read_and_preprocess_article, \
	get_nltk_sent_tokenizer, RegexSentenceTokenizer, Article, \
	get_sentences

article_dir = "/Users/boxiang/Documents/work/Baidu/projects/"\
	"med_translation/processed_data/crawler/nejm/articles_norm/"
sentence_dir = "/Users/boxiang/Documents/work/Baidu/projects/"\
	"med_translation/processed_data/crawler/nejm/sentences/"
if not os.path.exists(sentence_dir):
	os.makedirs(sentence_dir)

class Pair():
	def __init__(self, en, zh):
		self.en = en
		self.zh = zh
		self.align_paragraphs()

	def align_paragraphs(self):
		en = self.en 
		zh = self.zh
		len_en = len(en.kept_paragraphs)
		len_zh = len(zh.kept_paragraphs)

		if len_en == 0:
			print("{} is empty.".format(en.path))
			paragraph_pairs = "empty_en"

		elif len_zh == 0:
			print("{} is empty.".format(zh.path))
			paragraph_pairs = "empty_zh"

		elif len(en.kept_paragraphs) == \
			len(zh.kept_paragraphs):
			paragraph_pairs = [x for x in \
				zip(en.kept_paragraphs, zh.kept_paragraphs)]

		else:
			print("{}: en has {} paragraphs; zh has {} paragraphs".\
				format(en.path, len(en.kept_paragraphs), len(zh.kept_paragraphs)))
			paragraph_pairs = []

		self.paragraph_pairs = paragraph_pairs

# English:
article_paths = glob.glob("{}/*.en".format(article_dir))
article_paths = [x for x in article_paths if "撤稿" not in x]

nltk_sent_tokenizer = get_nltk_sent_tokenizer(article_paths, lang="en")
regex_sent_tokenizer = RegexSentenceTokenizer(regex="[^0-9]\.[0-9]{1,2}[0-9,-]*? ")


en_path="/Users/boxiang/Documents/work/Baidu/projects/med_translation/processed_data/crawler/nejm/articles_norm/接受多药物治疗的心房颤动患者中华法林和阿哌沙班的用药对比.en"
zh_path="/Users/boxiang/Documents/work/Baidu/projects/med_translation/processed_data/crawler/nejm/articles_norm/接受多药物治疗的心房颤动患者中华法林和阿哌沙班的用药对比.zh"

en = Article(en_path, lang="en", sent_tokenizers=[nltk_sent_tokenizer, regex_sent_tokenizer])
# len(en.kept_paragraphs)
# en.kept_paragraphs

regex_sent_tokenizer = RegexSentenceTokenizer(regex=u"[^！？。]+[！？。]?[”]*?")
zh = Article(zh_path, lang="zh", sent_tokenizers=[regex_sent_tokenizer])
# len(zh.kept_paragraphs)
# zh.kept_paragraphs

# en_path = "/Users/boxiang/Documents/work/Baidu/projects/med_translation/processed_data/crawler/nejm/articles_norm/伊布替尼作为慢性淋巴细胞白血病的初始治疗.en"
# zh_path = "/Users/boxiang/Documents/work/Baidu/projects/med_translation/processed_data/crawler/nejm/articles_norm/伊布替尼作为慢性淋巴细胞白血病的初始治疗.zh"

# en = Article(en_path, lang="en")
# len(en.kept_paragraphs)
# en.kept_paragraphs

# zh = Article(zh_path, lang="zh")
# len(zh.kept_paragraphs)
# zh.kept_paragraphs


differ = []
same = []
empty_zh = []
empty_en = []
n=0
for en_path in article_paths:
	# print("Article: {}".format(en_path), flush=True)
	zh_path = en_path.replace(".en", ".zh")
	try:
		en = Article(path=en_path, lang="en")
	except FileNotFoundError:
		print("{} does not exist.".format(en_path))
		en = None

	try: 
		zh = Article(path=zh_path, lang="zh")
	except FileNotFoundError:
		print("{} does not exist.".format(zh_path))
		zh = None

	if en and zh:
		pair = Pair(en, zh)

	if pair.paragraph_pairs == []:
		differ.append(pair)
	elif pair.paragraph_pairs == "empty_zh":
		empty_zh.append(pair)
	elif pair.paragraph_pairs == "empty_en":
		empty_en.append(pair)
	else:
		same.append(pair)
		n += 1

print(n) 


article_paths = glob.glob("{}/*.en".format(article_dir))
total = 0
marked = 0
for en_path in article_paths:

	try:
		en = Article(path=en_path, lang="en")

	except FileNotFoundError:
		print("{} does not exist.".format(en_path))
		en = None

	if en is None:
		continue

	for p in en.kept_paragraphs:
		if sorted(p.number.elements()) != []:
			marked += 1
		total += 1


# In [27]: total                                                                                                     
# Out[27]: 47271

# In [28]: marked                                                                                                    
# Out[28]: 27102

article_paths = glob.glob("{}/*.zh".format(article_dir))
total = 0
marked = 0
for en_path in article_paths:

	try:
		en = Article(path=en_path, lang="en")

	except FileNotFoundError:
		print("{} does not exist.".format(en_path))
		en = None

	if en is None:
		continue

	for p in en.kept_paragraphs:
		if sorted(p.number.elements()) != []:
			marked += 1
		total += 1

# In [30]: total                                                                                                     
# Out[30]: 49851

# In [31]: marked                                                                                                    
# Out[31]: 28828

# Baseline 241
# After removing 评论 and 出版时的编辑声明: 1104
# After removing "\n. opens in new tab\n": 1189
# After accounting for two words as date in English journal watch articles: 1275
# After adding more boilderplate: 1320