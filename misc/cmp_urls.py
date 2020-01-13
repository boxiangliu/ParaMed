import os
import re
import glob
import pandas as pd
pd.set_option('display.max_columns', 999)
import matplotlib
import matplotlib.pyplot as plt

new_dir = "../processed_data/crawler/nejm/urls/"
old_dir = "../processed_data/crawler/nejm/urls_old/"

# Read new urls:
container = []
new_files = glob.glob(f"{new_dir}/*/*.txt")
for fn in new_files:
	print(f"Filename: {fn}")
	container.append(pd.read_table(fn, header=None))
new = pd.concat(container)
new.columns = ["year", "month", \
	"id", "zh_title", "en_title", \
	"zh_url", "en_url"]
new = new[new["year"] != 2020] # Remove year 2020
print(f"Total number of new articles: {new.shape[0]}")

# Read old urls:
container = []
old_files = glob.glob(f"{old_dir}/*/*.txt")
for fn in old_files:
	print(f"Filename: {fn}")
	container.append(pd.read_table(fn, header=None))
old = pd.concat(container)
old.columns = ["zh_title", "zh_url", "en_url"]
print(f"Total number of old articles: {old.shape[0]}")

old["zh_url"].unique().shape
old["en_url"].unique().shape


new["in_old"] = new["zh_url"].apply(lambda x: x in old["zh_url"].tolist())
new[new["in_old"] == False][["year","month"]].drop_duplicates()

#    year  month
# 0  2019     12
# 0  2019     10
# 0  2019     11
# The new urls missing from the old are all from 10, 11, 12 of 2019. 


old["in_new"] = old["zh_url"].apply(lambda x: x in new["zh_url"].tolist())
old[old["in_new"] == False]

# The old urls missing from the new are all "Quick Take", or videos, which 
# do not have any text and should not be crawled at all. 
# For example: https://www.nejmqianyan.cn/article/YXQYdo005239