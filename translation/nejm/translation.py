#!/mnt/home/boxiang/software/anaconda2/envs/py3/bin/python
# -*- coding: utf-8 -*-
import os
import argparse
import logging
import time
import sys
sys.path.append("/mnt/home/boxiang/projects/med_translation/scripts/")
from googletrans import Translator
from utils.utils import	RegexSentenceTokenizer, Article

parser = argparse.ArgumentParser(description="Translate Chinese to English"\
								"sentences with Google API.")
parser.add_argument("--article_path_list", type=str, help="Path to articles.",
	default="../processed_data/crawler/nejm/translation/input_list")
parser.add_argument("--out_dir", type=str, help="Path to output directory.",
	default="../processed_data/crawler/nejm/translation/")
args = parser.parse_args()


def write_to_disk(sentences, out_fn):

	with open(out_fn, "w+") as f: 
		for s in sentences:
			f.write(s + "\n")


def setup():
	logging.info("{:=^30}".format(" Setup "))

	zh_regex_sent_tokenizer = \
		RegexSentenceTokenizer(regex=u"[^！？。]+[！？。]?[”]*?")
	zh_tokenizers = [zh_regex_sent_tokenizer]

	# Translator:
	translator = Translator()

	return zh_tokenizers, translator


def translate(text, translator, src="zh-cn", dest="en"):
	translation = []
	for t in text:
		print(t)
		x = translator.translate(t, src=src, dest=dest)
		translation.append(x.text.lower())
	return translation


def translate(text, translator, src="zh-cn", dest="en"):
	return [x.text.lower() for x in \
		translator.translate(text, src=src, dest=dest)]

def main():
	with open(path_list, "r") as pl:
		for line in pl:
			print(line)
			logging.info("{:=^30}".format(" Article "))
			start = time.time()

			zh_path = line.strip()
			print(zh_path)
			zh = Article(zh_path, lang="zh", sent_tokenizers=zh_tokenizers)
			print(zh.sentences)
			logging.info("Chinese: {}".format(zh_path))

			translation = translate(zh.sentences, translator)
			translation_time = time.time()
			logging.info("Translation Time: {:>7.2f}\t".\
				format(translation_time - start))

			out_fn = "{}_trans".format(zh_path)
			write_to_disk(translation, out_fn)


# Arguments:
path_list = args.article_path_list
out_dir = args.out_dir

if __name__ == "__main__":
	FORMAT = '%(message)s'
	log_fn = "{}/{}.log".format(out_dir, os.path.basename(path_list))
	logging.basicConfig(filename=log_fn, format=FORMAT)
	zh_tokenizers, translator = setup()
	main()