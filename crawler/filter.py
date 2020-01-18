import re
import sys
sys.path.append(".")
from utils.utils import read_article_urls

url_dir = "../processed_data/crawler/nejm/urls/"
article_dir = "../processed_data/crawler/nejm/articles/"

def read_article(fn):
	with open(fn, "r") as f: 
		x = f.readlines()
	return x


def stitch_zh(article):
	for i, _ in enumerate(article):
		if re.fullmatch("^[0-9,-]+\n$", article[i]):
			if article[i].endswith("\n"):
				article[i] = article[i].replace("\n", "")
			if article[i-1].endswith("\n"):
				article[i-1] = article[i-1].replace("\n", "")
		if re.fullmatch("^。$", article[i]):
			if article[i-1].endswith("\n"):
				article[i-1] = article[i-1].replace("\n", "")
	full_text = "".join(article)
	article = full_text.split("\n")
	return article


def filter_zh(article):
	keep = [True] * len(article)
	for i, text in enumerate(article):
		# Remove text in the middle:
		if re.match("图[0-9]{1,2}\.", text):
			keep[i] = keep[i+1] = False
		elif re.match("表[0-9]{1,2}\.", text):
			keep[i] = False
		elif text.startswith("*") or \
			text.startswith("†") or \
			text.startswith("‡") or \
			text.startswith("§") or \
			text.startswith("¶") or \
			text.startswith("‖") or \
			text.startswith("|"):
			keep[i] = False
		elif text == "":
			keep[i] = False

		# Remove text after:
		if text.startswith("Presented") or \
			text.startswith("Supported by") or \
			text.startswith("This case") or \
			text.startswith("Disclosure") or \
			"conflict of interest" in text or \
			text.startswith("I thank") or \
			text.startswith("We thank") or \
			text.startswith("From ") or \
			text.startswith("译者："):
			for j in range(i, len(keep)):
				keep[j] = False
			break # No need to look at subsequent lines.
	
	article_filt = []
	for a, k in zip(article, keep):
		if k == True:
			article_filt.append(a)

	return article_filt


meta = read_article_urls(url_dir)
meta = meta[meta["year"] != 2020] # Remove year 2020

for index, row in meta.iterrows():
	year = row["year"]
	month = row["month"]
	article_id = row["id"]
	in_fn = f"{article_dir}/{year}/{month:02}/{article_id}.full.zh"
	print(f"path: {in_fn}")
	article = read_article(in_fn)
	article = stitch_zh(article)
	article = filter_zh(article)

	out_fn = in_fn.replace(".full.", ".pp.")
	with open(out_fn, "w") as f: 
		for line in article:
			f.write(line + "\n")


def filter_en(article):
	