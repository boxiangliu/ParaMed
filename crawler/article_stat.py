import os
import re
import sys
import glob
from collections import defaultdict
import pandas as pd
pd.set_option('display.max_columns', 999)
import matplotlib
import matplotlib.pyplot as plt

sys.path.append(".")
from utils.utils import read_article_urls

urls_dir = "../processed_data/crawler/nejm/urls/"
in_dir = "../processed_data/crawler/nejm/articles/"
out_dir = "../processed_data/crawler/article_stat/"
os.makedirs(out_dir, exist_ok=True)

abbrev = {"cp": "Clinical Practice",
		"oa": "Original Article",
		"ra": "Review Article",
		"cpc": "Case Records",
		"sr": "Special Report",
		"ct": "Clinical Therapeutics",
		"jw.na": "Journal Watch",
		"clde": "Clinical Decisions",
		"cps": "Clinical Prob Solving",
		"p": "Perspective",
		"e": "Editorial",
		"cibr": "Clinical Implications\nof Basic Research",
		"icm": "Images in Clinical Med",
		"ms": "Medicine and Society",
		"c": "Correspondence",
		"sa": "Special Article",
		"x": "Correction",
		"hpr": "Health Policy Report"}

# Read article and urls:
article_urls = read_article_urls(urls_dir)
article_urls = article_urls[article_urls["year"] != 2020] # Remove year 2020

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
		if lang == "zh":
			fn = f"{in_dir}/{year}/{month:02}/{article_id}.pp.{lang}"
		else:
			fn = f"{in_dir}/{year}/{month:02}/{article_id}.full.{lang}"
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
			print(f"{fn} does not exist!")


article_stat = []
for i, (k, v) in enumerate(container.items()):
	article_stat.append(pd.DataFrame({"id": k, "year": \
		v["time"][0], "month": v["time"][1], \
		"zh_len": v["zh"]["len"], "en_len": v["en"]["len"], \
		"zh_m_en": v["zh_m_en"]}, index=[i]))
article_stat = pd.concat(article_stat)
article_stat["pct"] = article_stat.apply(lambda x: \
	2 * 100 * x["zh_m_en"] / (x["zh_len"] + x["en_len"]), axis=1)
article_stat["pct"].hist()
article_stat.sort_values("pct").tail(30).head(24)
article_stat[article_stat["id"].apply(lambda x: not x.startswith("oa") and not x.startswith("jw.na"))].sort_values("pct")
article_stat[article_stat["id"].apply(lambda x: x.startswith("oa"))]

article_id = "oa1212914"
container[article_id]
article_urls[article_urls["id"]==article_id]