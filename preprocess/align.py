import os
import re
import sys
import glob

import pandas as pd
import matplotlib.pyplot as plt
from dateutil import parser
from utils.utils import Container, get_article_as_lowercase_string, \
	get_nltk_sent_tokenizer, RegexSentenceTokenizer

article_dir = "/Users/boxiang/Documents/work/Baidu/projects/"\
	"med_translation/processed_data/crawler/nejm/articles_norm/"
sentence_dir = "/Users/boxiang/Documents/work/Baidu/projects/"\
	"med_translation/processed_data/crawler/nejm/sentences/"
if not os.path.exists(sentence_dir):
	os.makedirs(sentence_dir)

class Article():
	def __init__(self, path, lang, sent_tokenizers=None):
		self.path = path
		self.lang = lang
		self.article = get_article_as_lowercase_string(path)
		self.paragraphs = self.article.split("\n")
		self.filter_paragraphs()
		self.sent_tokenizers = sent_tokenizers \
			if isinstance(sent_tokenizers, list) \
			else [sent_tokenizers] 
		self.sentences = self.get_sentences(
			self.sent_tokenizers, self.paragraphs)


	def get_sentences(self, sent_tokenizers, texts):
		if sent_tokenizers[0] is None:
			return []

		if not isinstance(texts, list):
			texts = [texts]

		for tokenizer in sent_tokenizers:
			sentences = []
			for t in texts:
				s = tokenizer.tokenize(t)
				sentences += s
			texts = sentences
		
		return sentences

	def is_boilerplate(self, text):

		lang = self.lang
		text = text.strip()

		def is_date(text):
			try:
				parser.parse(text)
				return True
			except ValueError:
				return False

		def is_reviewer_intro(text):
			last_three_words = " ".join(text.split(" ")[-3:])
			last_two_words = last_three_words[1:]
			if is_date(last_three_words) or \
				is_date(last_two_words):
				if "reviewing" in text:
					return True

			return False

		english_boilerplates = ["access provided by",
			"access provided by lane medical library, "\
			"stanford university med center",
			"lane medical library, stanford university med center",
			"subscribe", 
			"or renew",
			"institution: stanford university",
			". opens in new tab",
			".)",
			]

		chinese_boilerplates = ["图1.", "图2.", "图3.", "图4.",
			"图5.", "表1.", "表2.", "表3.", "表4.", "表5."]

		if lang == "en":

			if is_date(text):
				return True
			elif is_reviewer_intro(text):
				return True
			elif text in english_boilerplates:
				return True

			return False

		elif lang == "zh":

			if text in chinese_boilerplates:
				return True
			elif text.startswith("评论") \
				and text.endswith("评论"):
				return True
			elif text.startswith("出版时的编辑声明") \
				and text.endswith("出版时的编辑声明"):
				return True
			else:
				return False

	def filter_paragraphs(self):

		kept_paragraphs = []
		filtered_paragraphs = []
		for para in self.paragraphs:

			if para.strip() == "":
				continue

			if self.is_boilerplate(para):
				filtered_paragraphs.append(para)
			else:
				kept_paragraphs.append(para)


		def find_and_remove_grant(paragraphs):
			if paragraphs[-1].strip().startswith("supported by"):
				return paragraphs.pop()
			else:
				return None

		grant = find_and_remove_grant(kept_paragraphs)
		if grant is not None:
			filtered_paragraphs.append(grant)

		self.kept_paragraphs = kept_paragraphs
		self.filtered_paragraphs = filtered_paragraphs


	def get_paragraph_lengths(self):
		if self.lang == "en":
			lengths = [len(para.split(" ")) \
				for para in self.paragraphs \
				if len(para) != 0]

		elif self.lang == "zh":
			lengths = []
			for para in self.paragraphs:
				para = re.sub("[a-z]", "", para)
				length = len(para)
				if length != 0: 
					lengths.append(len(para))

		else:
			raise ValueError("Language not supported: {}".\
				format(self.lang))

		return lengths


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


class Pair():
	def __init__(self, en, zh):
		self.en = en
		self.zh = zh
		self.align()

	def align(self):
		en = self.en 
		zh = self.zh
		
		if len(en.kept_paragraphs) == \
			len(zh.kept_paragraphs):
			paragraph_pairs = [x for x in \
				zip(en.kept_paragraphs, zh.kept_paragraphs)]
		else:
			print("{}: en has {} paragraphs; zh has {} paragraphs".\
				format(en.path, len(en.kept_paragraphs), len(zh.kept_paragraphs)))
			paragraph_pairs = []

		self.paragraph_pairs = paragraph_pairs

# English:
en_path="/Users/boxiang/Documents/work/Baidu/projects/med_translation/processed_data/crawler/nejm/articles_norm/接受多药物治疗的心房颤动患者中华法林和阿哌沙班的用药对比.en"
zh_path="/Users/boxiang/Documents/work/Baidu/projects/med_translation/processed_data/crawler/nejm/articles_norm/接受多药物治疗的心房颤动患者中华法林和阿哌沙班的用药对比.zh"

en = Article(en_path, lang="en")
len(en.kept_paragraphs)
en.kept_paragraphs

zh = Article(zh_path, lang="zh")
len(zh.kept_paragraphs)
zh.kept_paragraphs

en_path = "/Users/boxiang/Documents/work/Baidu/projects/med_translation/processed_data/crawler/nejm/articles_norm/伊布替尼作为慢性淋巴细胞白血病的初始治疗.en"
zh_path = "/Users/boxiang/Documents/work/Baidu/projects/med_translation/processed_data/crawler/nejm/articles_norm/伊布替尼作为慢性淋巴细胞白血病的初始治疗.zh"

en = Article(en_path, lang="en")
len(en.kept_paragraphs)
en.kept_paragraphs

zh = Article(zh_path, lang="zh")
len(zh.kept_paragraphs)
zh.kept_paragraphs


article_paths=glob.glob("{}/*.en".format(article_dir))
n = 0
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

	if pair.paragraph_pairs != []:
		n += 1

print(n)