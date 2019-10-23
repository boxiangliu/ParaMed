import os
import re
import sys
import glob
import string

import numpy as np
from googletrans import Translator
from nltk.corpus import stopwords
from collections import Counter
from utils.utils import	get_nltk_sent_tokenizer, \
	RegexSentenceTokenizer, Article

article_dir = "/Users/boxiang/Documents/work/Baidu/projects/"\
	"med_translation/processed_data/crawler/nejm/articles_norm/"

nltk_sent_tokenizer = get_nltk_sent_tokenizer(article_paths, lang="en")
regex_sent_tokenizer = RegexSentenceTokenizer(regex="[^0-9]\.[0-9]{1,2}[0-9,-]*? ")

translator = Translator()
def translate(text, translator, src="zh-cn", dest="en"):
	return [x.text.lower() for x in \
		translator.translate(text, src=src, dest=dest)]


en_path="/Users/boxiang/Documents/work/Baidu/projects/med_translation/processed_data/crawler/nejm/articles_norm/接受多药物治疗的心房颤动患者中华法林和阿哌沙班的用药对比.en"
zh_path="/Users/boxiang/Documents/work/Baidu/projects/med_translation/processed_data/crawler/nejm/articles_norm/接受多药物治疗的心房颤动患者中华法林和阿哌沙班的用药对比.zh"

en = Article(en_path, lang="en", sent_tokenizers=[nltk_sent_tokenizer, regex_sent_tokenizer])

regex_sent_tokenizer = RegexSentenceTokenizer(regex=u"[^！？。]+[！？。]?[”]*?")
zh = Article(zh_path, lang="zh", sent_tokenizers=[regex_sent_tokenizer])

translation = translate(zh.kept_paragraphs, translator)
en_stopwords = set(stopwords.words("english"))


def remove_punctuation_and_stopwords(text, stopwords):
	text = text.translate(str.maketrans("", "", string.punctuation))
	text = text.split(" ")
	return [x for x in text if x not in stopwords]

zh_words = remove_punctuation_and_stopwords(translation[0], en_stopwords)
zh_tf = Counter(zh_words)

en_words = remove_punctuation_and_stopwords(en.kept_paragraphs[0], en_stopwords)
en_tf = Counter(en_words)

def get_semantic_dist(en_para, zh_para):
	tokens = roberta.encode(en_para, zh_para)
	
	# contradiction: Log(Pc)
	# neural: Log(Pn)
	# entailment: Log(Pe)
	logpc, logpn, logpe = roberta.predict('mnli', tokens)[0].tolist()
	return logpc - logpn - 2*logpe 


dist = np.ndarray([len(en_kept_paragraphs), len(translation)])
for i, _ in enumerate(en_kept_paragraphs):
	for j, _ in enumerate(translation):
		d1 = dist[i-1, j-1] + get_semantic_dist(en_kept_paragraphs[i], translation[j]) if i > 0 and j > 0 else 0 # substitution
		d2 = dist[i-1, j] 
		similarity[i,j] = get_similarity(en_para, zh_para)

# Run on Asimov:
import torch
roberta = torch.hub.load("pytorch/fairseq", "roberta.large.mnli")
tokens = roberta.encode('Roberta is a heavily optimized version of BERT.', 'Roberta is not very optimized.')