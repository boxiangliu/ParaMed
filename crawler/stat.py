import os
import re
import glob
import pandas as pd
pd.set_option('display.max_columns', 999)
import matplotlib
import matplotlib.pyplot as plt

in_dir = "../processed_data/crawler/nejm/urls/"
out_dir = "../processed_data/crawler/stat/"
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
container = []
article_files = glob.glob(f"{in_dir}/*/*.txt")
for fn in article_files:
	print(f"Filename: {fn}")
	container.append(pd.read_table(fn, header=None))
articles = pd.concat(container)
articles.columns = ["year", "month", \
	"id", "zh_title", "en_title", \
	"zh_url", "en_url"]
articles = articles[articles["year"] != 2020] # Remove year 2020
print(f"Total number of articles: {articles.shape[0]}")

# Check all articles are unique:
assert articles["id"].unique().shape[0] == articles.shape[0],
	"Duplicate articles exists."

# Plot article count by year:
year_count = articles.groupby("year").\
	agg(count=pd.NamedAgg("year", "count")).\
	reset_index()

fig, (ax1, ax2) = plt.subplots(2,1)
ax1.clear()
ax1.bar("year", "count", data=year_count)
ax1.spines['right'].set_visible(False)
ax1.spines['top'].set_visible(False)
ax1.set_xticks(ticks=year_count["year"])
ax1.set_xticklabels(labels=year_count["year"])


# Plot count by article type:
articles["type_abbr"] = articles["id"].apply(lambda x: re.sub("[0-9%]+", "", x))
articles["type"] = articles["type_abbr"].apply(lambda x: abbrev[x])
type_count = articles.groupby("type").\
	agg(count=pd.NamedAgg("type", "count")).\
	reset_index()
type_count.sort_values(by="count", inplace=True, ascending=False)

ax2.clear()
ax2.bar("type", "count", data=type_count)
ax2.set_xticklabels(labels=type_count["type"], rotation=90, linespacing=0.95)
ax2.semilogy()
ax2.spines['right'].set_visible(False)
ax2.spines['top'].set_visible(False)


# Save figure:
fig.set_size_inches(5,5)
fig.tight_layout()
fig.savefig(f"{out_dir}/article_statistics.pdf")