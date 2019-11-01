import os
import re
import sys
import glob
import string
import torch

import numpy as np
from googletrans import Translator
from nltk.corpus import stopwords
from collections import Counter
from utils.utils import	get_nltk_sent_tokenizer, \
	RegexSentenceTokenizer, Article

article_dir = "../processed_data/crawler/nejm/articles_norm/"
article_paths = glob.glob("{}/*.en".format(article_dir))
article_paths = [x for x in article_paths if "撤稿" not in x]

nltk_sent_tokenizer = get_nltk_sent_tokenizer(article_paths, lang="en")
en_regex_sent_tokenizer = RegexSentenceTokenizer(regex="[^0-9]\.[0-9]{1,2}[0-9,-]*? ")

translator = Translator()
def translate(text, translator, src="zh-cn", dest="en"):
	return [x.text.lower() for x in \
		translator.translate(text, src=src, dest=dest)]


en_path="../processed_data/crawler/nejm/articles_norm/接受多药物治疗的心房颤动患者中华法林和阿哌沙班的用药对比.en"
zh_path="../processed_data/crawler/nejm/articles_norm/接受多药物治疗的心房颤动患者中华法林和阿哌沙班的用药对比.zh"

en = Article(en_path, lang="en", sent_tokenizers=[nltk_sent_tokenizer, en_regex_sent_tokenizer])

zh_regex_sent_tokenizer = RegexSentenceTokenizer(regex=u"[^！？。]+[！？。]?[”]*?")
zh = Article(zh_path, lang="zh", sent_tokenizers=[zh_regex_sent_tokenizer])

translation = translate(zh.sentences, translator)
en_stopwords = set(stopwords.words("english"))


def remove_punctuation_and_stopwords(text, stopwords):
	text = text.translate(str.maketrans("", "", string.punctuation))
	text = text.split(" ")
	return [x for x in text if x not in stopwords]


roberta = torch.hub.load('pytorch/fairseq', 'roberta.large.mnli')
roberta.eval()  # disable dropout for evaluation
roberta.cuda()

def get_semantic_score(en_para, zh_para):
	if isinstance(en_para, list):
		en_para = " ".join(en_para)
	if isinstance(zh_para, list):
		zh_para = " ".join(zh_para)

	tokens = roberta.encode(en_para, zh_para)
	
	# contradiction: Log(Pc)
	# neural: Log(Pn)
	# entailment: Log(Pe)
	logpc, logpn, logpe = roberta.predict('mnli', tokens)[0].tolist()
	return 2*logpe - logpc - logpn


def fill_table(text1, text2):
	n1 = len(text1) + 1
	n2 = len(text2) + 1
	score = np.zeros(shape=(n1, n2))
	path_x = np.zeros(shape=(n1, n2), dtype=np.int8)
	path_y = np.ndarray(shape=(n1, n2), dtype=np.int8)


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


def backtrace(path_x, path_y, text1, text2):
	i, j = path_x.shape[0] - 1, path_x.shape[1] - 1
	index_pairs = [(i,j)]
	sentence_pairs = []
	while i > 0 or j > 0:
		oi, oj = path_x[i,j], path_y[i,j]
		index_pairs.append((oi,oj))
		sent1 = " ".join(text1[oi:i])
		sent2 = " ".join(text2[oj:j])
		sentence_pairs.append((sent1, sent2))
		i, j = oi, oj
	return index_pairs[-1::-1], sentence_pairs[-1::-1]


score, path_x, path_y = fill_table(en.sentences, translation)
index_pairs, sentence_pairs = backtrace(path_x, path_y, en.sentences, zh.sentences)
index_pairs
sentence_pairs


en_path="../processed_data/crawler/nejm/articles_norm/1型和2型糖尿病患者的死亡率和心血管疾病结局.en"
zh_path="../processed_data/crawler/nejm/articles_norm/1型和2型糖尿病患者的死亡率和心血管疾病结局.zh"
en = Article(en_path, lang="en", sent_tokenizers=[nltk_sent_tokenizer, en_regex_sent_tokenizer])
zh = Article(zh_path, lang="zh", sent_tokenizers=[zh_regex_sent_tokenizer])

translation = translate(zh.sentences, translator)

score, path_x, path_y = fill_table(en.sentences, translation)
index_pairs, sentence_pairs = backtrace(path_x, path_y, en.sentences, zh.sentences)
index_pairs
sentence_pairs

# Correct case:
 # ('the specific codes are listed in table s1 in the supplementary appendix, available with the full text of this article at nejm.org.',
 #  '这些特定的编码见补充附录表s1，补充附录与本文全文均可在nejm.org获取。',
 #  8.890294075012207),
 # ('the last date for inclusion in the current analysis cohort was december 31, 2012.',
 #  '',
 #  1.8831095695495605),
 # ('patients were followed until december 31, 2013, for all outcomes, except for death from any cause, for which follow-up ended on december 31, 2014.',
 #  '本分析队列纳入了2012年12月31日以前的患者，然后对所有结局随访至2013年12月31日，其中任何原因死亡除外，该结局随访至2014年12月31日。',



 # Incorrect case:
 #  ('', '参与者一旦发生非致死性结局（即使在进入ndr之前），其数据截尾于该结局发生时。', -1.8566284775733948),
 # ('data on persons who had a nonfatal outcome, even before inclusion in the ndr, were censored at the time of the outcome, and persons with that outcome were not included in the numerator or denominator for that specific outcome but could be included in the numerator and denominator for fatal and other nonfatal outcomes.',
 #  '有此结局的参与者，不会被纳入到该结局的分子或分母，但可以被纳入到致死性或其他非致死性结局的分子或者分母中。',
 #  9.568348407745361),


 #  ('the epidemiologic definitions that we used have been validated as accurate in 97% of cases, as reported previously.36 (see the supplementary appendix for a more detailed discussion of this issue.37) second, we cannot exclude the possibility that secular trends, such as evolving diagnostic thresholds or admissions criteria, could have influenced the changes in event rates that we have reported.',
 #  '据此前报道36，我们采用的流行病学定义被证实在97%的病例中是准确的（本问题的详细讨论见补充附录37）。',
 #  11.395211219787598),
 # ('',
 #  '其次，我们无法排除某些长期变化趋势可能对我们报道的事件发生率的变化产生影响，譬如诊断阈值或入院指标的变化。',
 #  -5.881786823272705),
