#!/mnt/home/boxiang/software/anaconda2/envs/py3/bin/python
# -*- coding: utf-8 -*-
import os
import re
import sys
import glob
import string
import argparse
import logging
import time
import sys
sys.path.append("/mnt/home/boxiang/projects/med_translation/scripts/")

import numpy as np
from googletrans import Translator
from nltk.corpus import stopwords
from collections import Counter
from utils.utils import	get_nltk_sent_tokenizer, \
	RegexSentenceTokenizer, Article

import torch

parser = argparse.ArgumentParser(description="Align Chinese and English"\
								"sentences using semantic meaning.")
parser.add_argument("--article_dir", type=str, help="Path to all articles.",
	default="../processed_data/crawler/nejm/articles_norm/")
parser.add_argument("--article_path_list", type=str, help="Path to articles.")
parser.add_argument("--out_dir", type=str, help="Path to output directory.")
args = parser.parse_args()


# EXample paths:
# en_path = "../processed_data/crawler/nejm/articles_norm/"\
# 	"接受多药物治疗的心房颤动患者中华法林和阿哌沙班的用药对比.en"

# zh_path = "../processed_data/crawler/nejm/articles_norm/"\
# 	"接受多药物治疗的心房颤动患者中华法林和阿哌沙班的用药对比.zh"


def get_article_paths(article_dir):
	article_paths = glob.glob("{}/*.en".format(article_dir))
	article_paths = [x for x in article_paths if "撤稿" not in x]
	return article_paths


def remove_punctuation_and_stopwords(text, stopwords):
	text = text.translate(str.maketrans("", "", string.punctuation))
	text = text.split(" ")
	return [x for x in text if x not in stopwords]


def get_semantic_score(en_sents, zh_sents):
	if isinstance(en_sents, list):
		en_sents = " ".join(en_sents)
	if isinstance(zh_sents, list):
		zh_sents = " ".join(zh_sents)

	tokens = roberta.encode(en_sents, zh_sents)
	
	# contradiction: Log(Pc)
	# neural: Log(Pn)
	# entailment: Log(Pe)
	logpc, logpn, logpe = roberta.predict('mnli', tokens)[0].tolist()
	return 2*logpe - logpc - logpn


def fill_table(text1, text2):
	n1 = len(text1) + 1
	n2 = len(text2) + 1
	score = np.zeros(shape=(n1, n2))
	path_x = np.zeros(shape=(n1, n2), dtype=np.int32)
	path_y = np.ndarray(shape=(n1, n2), dtype=np.int32)


	for j in range(0,n2):
		for i in range(0,n1):

			print((i,j))

			# substitution:
			s1 = score[i-1, j-1] + \
				get_semantic_score(text1[i-1], text2[j-1]) \
				if i > 0 and j > 0 else 0
			# deletion
			s2 = score[i-1, j] + \
				get_semantic_score(text1[i-1], "") \
				if i > 0 else 0
			# insertion
			s3 = score[i, j-1] + \
				get_semantic_score("", text2[j-1]) \
				if j > 0 else 0
			# contraction
			s4 = score[i-2, j-1] + \
				get_semantic_score(text1[i-2:i], text2[j-1]) \
				if i > 1 and j > 0 else 0
			# expansion
			s5 = score[i-1, j-2] + \
				get_semantic_score(text1[i-1], text2[j-2:j]) \
				if i > 0 and j > 1 else 0
			# melding
			# s6 = score[i-2, j-2] + \
			# 	get_semantic_score(text1[i-2:i], text2[j-2:j]) \
			# 	if i > 1 and j > 1 else 0
			max_score = max(s1, s2, s3, s4, s5)

			if max_score == 0:
				score[i, j] = 0

			elif max_score == s1:
				score[i, j] = s1
				path_x[i, j] = i - 1
				path_y[i, j] = j - 1

			elif max_score == s2:
				score[i, j] = s2
				path_x[i, j] = i-1
				path_y[i, j] = j

			elif max_score == s3: 
				score[i, j] = s3
				path_x[i, j] = i
				path_y[i, j] = j-1

			elif max_score == s4:
				score[i, j] = s4
				path_x[i, j] = i-2
				path_y[i, j] = j-1

			elif max_score == s5:
				score[i, j] = s5
				path_x[i, j] = i-1
				path_y[i, j] = j-2

			# elif max_score == s6:
			# 	score[i, j] = s6
			# 	path_x[i, j] = i-2
			# 	path_y[i, j] = j-2

			else:
				raise ValueError

	return score, path_x, path_y


def backtrace(path_x, path_y, score, text1, text2):
	i, j = path_x.shape[0] - 1, path_x.shape[1] - 1
	index_pairs = []
	sentence_pairs = []
	while i > 0 or j > 0:
		oi, oj = path_x[i,j], path_y[i,j]
		index_pairs.append([oi,oj])
		sent1 = " ".join(text1[oi:i])
		sent2 = " ".join(text2[oj:j])
		pair_score = score[i,j] - score[oi,oj]
		sentence_pairs.append([sent1, sent2, pair_score])
		i, j = oi, oj
	return index_pairs[-1::-1], sentence_pairs[-1::-1]


def write_to_disk(index_pairs, sentence_pairs, out_fn):
	# print(index_pairs)
	# print(len(index_pairs))
	# print(sentence_pairs)
	# print(len(sentence_pairs))

	assert len(index_pairs) == len(sentence_pairs), \
		"len(index_pairs) != len(sentence_pairs)"

	with open(out_fn, "w+") as f: 
		for i in range(0, len(index_pairs)):
			output = "\t".join([str(x) for x in index_pairs[i]] \
				+ [str(x) for x in sentence_pairs[i]]) + "\n"
			f.write(output)


def setup():
	logging.info("{:=^30}".format(" Setup "))
	# Article paths:
	article_paths = get_article_paths(article_dir)

	# Tokenizers:
	en_nltk_sent_tokenizer = get_nltk_sent_tokenizer(article_paths, lang="en")
	en_regex_sent_tokenizer = \
		RegexSentenceTokenizer(regex="[^0-9]\.[0-9]{1,2}[0-9,-]*? ")
	en_tokenizers = [en_nltk_sent_tokenizer, en_regex_sent_tokenizer]
	zh_regex_sent_tokenizer = \
		RegexSentenceTokenizer(regex=u"[^！？。]+[！？。]?[”]*?")
	zh_tokenizers = [zh_regex_sent_tokenizer]

	# Translator:
	translator = Translator()

	# Roberta: 
	roberta = torch.hub.load('pytorch/fairseq', 'roberta.large.mnli')
	roberta.eval()  # disable dropout for evaluation
	roberta.cuda()


	return en_tokenizers, zh_tokenizers, translator, roberta


def main():
	with open(path_list, "r") as pl:
		for line in pl:
			logging.info("{:=^30}".format(" Article "))
			start = time.time()

			en_path, zh_path = line.strip().split("\t")
			en = Article(en_path, lang="en", sent_tokenizers=en_tokenizers)
			zh = Article(zh_path, lang="zh", sent_tokenizers=zh_tokenizers)
			logging.info("English: {}".format(en_path))
			logging.info("Chinese: {}".format(zh_path))

			translation = translate(zh.sentences, translator)
			translation_time = time.time()

			score, path_x, path_y = fill_table(en.sentences, translation)
			index_pairs, sentence_pairs = backtrace(path_x, path_y, \
				score, en.sentences, zh.sentences)
			dp_time = time.time()
			logging.info("Translation Time: {:>7.2f}\tDP Time: {:>7.2f}".\
				format(translation_time - start, dp_time - translation_time))

			out_fn = "{}/{}.pair".format(out_dir, \
				os.path.basename(en_path.replace(".en","")))
			write_to_disk(index_pairs, sentence_pairs, out_fn)


# Arguments:
article_dir = args.article_dir
path_list = args.article_path_list
out_dir = args.out_dir


if __name__ == "__main__":
	FORMAT = '%(message)s'
	log_fn = "{}/{}.log".format(out_dir, os.path.basename(path_list))
	logging.basicConfig(filename=log_fn, format=FORMAT)
	en_tokenizers, zh_tokenizers, translator, roberta = setup()
	main()