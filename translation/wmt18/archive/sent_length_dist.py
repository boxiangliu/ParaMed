import argparse
from collections import defaultdict
import pandas as pd
import matplotlib
matplotlib.use('tkagg')
import matplotlib.pyplot as plt
import os

parser = argparse.ArgumentParser(
	description="Plot the distribution of sequence length")
parser.add_argument("--files", type=str, 
	help="Comma separated list of name:file entries."\
		 "For example, UN_zh:UNcorpus.zh, UN_en:UNcorpus.en",
	default="nejm_en:/mnt/home/boxiang/projects/med_translation/processed_data/preprocess/sentences_concat/nejm.tok.en,"\
			"nejm_zh:/mnt/home/boxiang/projects/med_translation/processed_data/preprocess/sentences_concat/nejm.tok.zh,"\
			"wmt18_en:/mnt/data/boxiang/wmt18/corpus/corpus.en,"\
			"wmt18_zh:/mnt/data/boxiang/wmt18/corpus/corpus.zh")
parser.add_argument("--out_dir", type=str,
	help="Output directory.",
	default="/mnt/home/boxiang/projects/med_translation/"\
			"processed_data/translation/wmt18/sent_length_dist/")
args=parser.parse_args()

files = dict([x.split(":") for x in \
	args.files.strip().split(",")])
out_dir = args.out_dir
os.makedirs(out_dir, exist_ok=True)

sent_length = defaultdict(list)
for name, file in files.items():
	print("Processing {}".format(name))
	with open(file, "r") as fin:
		for i, line in enumerate(fin):
			if i % 1000000 == 0:
				print("Processed {} lines.".format(i))
			split_line = line.strip().split(" ")
			sent_length[name].append(len(split_line))

	print("Writing to {}".format(name))
	with open(file + ".sent_len", "w+") as fout:
		for length in sent_length[name]:
			fout.write(str(length) + "\n")

for name, length in sent_length.items():
	plt.hist(sent_length[name], bins=20, 
		alpha=0.5, label=name, log=True)
plt.legend(loc='upper right')
plt.savefig("{}/{}.png".format(out_dir,"hist"))