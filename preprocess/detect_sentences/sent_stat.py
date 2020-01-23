import os
import re
import sys
import glob
from collections import defaultdict
import pandas as pd
pd.set_option('display.max_columns', 999)
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
sys.path.append(".")
from utils.utils import read_article_urls, abbrev


urls_dir = "../processed_data/crawler/nejm/urls/"
base_dir = "../processed_data/preprocess/sentences/"
punkt_dir = f"{base_dir}/punkt/"
eserix_dir = f"{base_dir}/eserix/"
out_dir = "../processed_data/preprocess/sent_stat/"
os.makedirs(out_dir, exist_ok=True)


def get_article_length(in_dir, article_urls, status):
	container = defaultdict(lambda: \
		{"time": None, 
		"zh": {"text": None, "len": None},
		"en": {"text": None, "len": None},
		"zh_m_en": None})

	for index, row in article_urls.iterrows():
		for lang in ["zh", "en"]:
			year = row["year"]
			month = row["month"]
			article_id = row["id"]
			fn = f"{in_dir}/{article_id}.{status}.{lang}"
			print(f"path: {fn}")

			try:
				with open(fn, "r") as f: text = f.readlines()
				length = len(text)
				container[article_id]["time"] = (int(year),int(month))
				container[article_id][lang]["text"] = text
				container[article_id][lang]["len"] = length

				if container[article_id]["zh"]["len"] != None and \
					container[article_id]["en"]["len"] != None:
					container[article_id]["zh_m_en"] = \
						container[article_id]["zh"]["len"] - \
						container[article_id]["en"]["len"]
			except:
				print("Article not found.")

	article_stat = []
	for i, (k, v) in enumerate(container.items()):
		article_stat.append(pd.DataFrame({"id": k, "year": \
			v["time"][0], "month": v["time"][1], \
			"zh_len": v["zh"]["len"], "en_len": v["en"]["len"], \
			"zh_m_en": v["zh_m_en"]}, index=[i]))
	article_stat = pd.concat(article_stat)
	article_stat["type_abbr"] = article_stat["id"].apply(lambda x: re.sub("[0-9%]+", "", x))
	article_stat["status"] = status
	try:
		article_stat["abs_diff"] = article_stat["zh_m_en"].apply(lambda x: abs(x))
	except TypeError:
		print("NaN found in zh_m_en.")
	return article_stat


def p1():
	p1_data = pd.merge(punkt[["id", "abs_diff"]], eserix[["id", "abs_diff"]], \
		on="id", suffixes=["_punkt", "_eserix"])
	p1_data = pd.melt(p1_data, id_vars=["id"], \
		value_name="abs_diff", var_name="tokenizer")

	fig, ax = plt.subplots(1,1)
	ax.clear()
	sns.boxplot(x="tokenizer", y="abs_diff", data=p1_data, showfliers=False)
	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)
	ax.set_xlabel("Sentence Tokenizer")
	ax.set_ylabel("|No. zh sent. - No. en sent.|")
	ax.set_xticklabels(["punkt", "eserix"])
	fig.set_size_inches(3,3)
	fig.tight_layout()
	fig.savefig(f"{out_dir}/cmp_punkt_eserix.pdf")

# Plot:
def punkt_plot():
	fig, ax = plt.subplots(1,1)
	ax.clear()
	plt.scatter(x="zh_len", y="en_len", data=punkt)
	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)
	ax.set_xlabel("Chinese Sentence Length")
	ax.set_ylabel("English Sentence Length")
	xlim = ylim = ax.get_xlim()
	plt.plot(xlim, ylim, color="red", linestyle="dashed")
	fig.set_size_inches(3,3)
	fig.tight_layout()
	fig.savefig(f"{out_dir}/punkt.pdf")

def eserix_plot():
	fig, ax = plt.subplots(1,1)
	ax.clear()
	plt.scatter(x="zh_len", y="en_len", data=eserix)
	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)
	ax.set_xlabel("Chinese Sentence Length")
	ax.set_ylabel("English Sentence Length")
	xlim = ylim = ax.get_xlim()
	plt.plot(xlim, ylim, color="red", linestyle="dashed")
	fig.set_size_inches(3,3)
	fig.tight_layout()
	fig.savefig(f"{out_dir}/eserix.pdf")


# Read article and urls:
article_urls = read_article_urls(urls_dir)
article_urls = article_urls[article_urls["year"] != 2020] # Remove year 2020

punkt = get_article_length(punkt_dir, article_urls, "filt")
punkt["abs_diff"].describe()
# count    1973.000000
# mean        2.655347
# std         3.751648
# min         0.000000
# 25%         1.000000
# 50%         1.000000
# 75%         3.000000
# max        38.000000

eserix = get_article_length(eserix_dir, article_urls, "filt")
eserix["abs_diff"].describe()
# count    1973.000000
# mean        1.538267
# std         2.883678
# min         0.000000
# 25%         0.000000
# 50%         0.000000
# 75%         2.000000
# max        27.000000

p1()
punkt_plot()
eserix_plot()