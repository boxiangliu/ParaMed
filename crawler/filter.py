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

# Stitch two or more sentences into one
# Why? Because sometime a single sentence 
# are broken into muliple piece on the website.
def stitch(article, lang):
	if lang == "zh":
		for i, _ in enumerate(article):
			# A line with only numbers (i.e citation)
			if re.fullmatch("^[0-9,-]+\n$", article[i]):
				if article[i].endswith("\n"):
					article[i] = article[i].replace("\n", "")
				if article[i-1].endswith("\n"):
					article[i-1] = article[i-1].replace("\n", "")
			# A line with open a period
			if re.fullmatch("^。$", article[i]):
				if article[i-1].endswith("\n"):
					article[i-1] = article[i-1].replace("\n", "")

	elif lang == "en":
		for i, _ in enumerate(article):
			# A line with a hyperlink
			if article[i].strip() == ". opens in new tab":
				article[i] = ""
				if article[i-1].endswith("\n"):
					article[i-1] = article[i-1].replace("\n", "")

	full_text = "".join(article)
	article = full_text.split("\n")
	return article


def filter(article, article_type, lang):
	keep = [True] * len(article)

	# Remove correspondence and 
	# image in clinical medicine
	if article_type in ["c", "icm"]: 
		return [] 

	if lang == "zh":
		for i, text in enumerate(article):

			#############################
			# Remove text in the middle #
			#############################
			# Remove tables and figures
			if re.match("图[0-9]{1,2}\.", text):
				keep[i] = keep[i+1] = False
			elif re.match("表[0-9]{1,2}\.", text):
				keep[i] = False

			# Remove table captions
			elif text.startswith("*") or \
				text.startswith("†") or \
				text.startswith("‡") or \
				text.startswith("§") or \
				text.startswith("¶") or \
				text.startswith("‖") or \
				text.startswith("|"):
				keep[i] = False

			# Remove empty lines
			elif text.strip() == "":
				keep[i] = False

			######################
			# Remove text before #
			######################
			if article_type == "clde":
				if text.strip() == "案例摘要" or \
					text.strip() == "病例摘要":
					for j in range(i):
						keep[j] = False

			#####################
			# Remove text after #
			#####################
			if article_type == "jw.na": # Journal Watch
				if text.startswith("出版时") or \
					text.startswith("引文"):
					for j in range(i, len(keep)):
						keep[j] = False
					break

			# Original Article
			# Review Article
			# Case Records
			# Perspective
			# Editorial
			# Clinical Problem solving
			# Clinical Implications of Basic Research
			# Special report
			# Special article
			# Clinical therapeutics
			# Health policy report
			# Clinical practice
			# Medicine and Society
			elif article_type in ["oa", "ra", "cpc", "p", "ms",\
				"e", "cps", "cibr", "sr", "sa", "ct", "hpr", "cp"] : 
				if text.startswith("Disclosure") or \
					text.startswith("译者") or \
					text.startswith("作者信息"):
					for j in range(i, len(keep)):
						keep[j] = False
					break
			# Corrections
			elif article_type == "x": 
				if text.startswith("译者"):
					for j in range(i, len(keep)):
						keep[j] = False
					break
			# Clinical Decisions
			elif article_type == "clde":
				if text.startswith("选项2"):
					for j in range(i, len(keep)):
						keep[j] = False
					break



	elif lang == "en":
		for i, text in enumerate(article):

			#############################
			# Remove text in the middle #
			#############################
			# Remove Table and Figure
			if re.match("Table [0-9]{1,2}\.", text) or \
				re.match("Figure [0-9]{1,2}\.", text):
				keep[i] = keep[i+1] = False
			# Remove video and audio interviews:
			elif text.strip() == "Video" or \
				text.strip() == "Audio Interview":
				keep[i] = keep[i+1] = False
			# Remove QUICK TAKE:
			elif text.strip() == "QUICK TAKE":
				keep[i] = keep[i+1] = keep[i+2] = False
			# Remove intro and other text:
			elif text.strip() == "Letters" or \
				text.strip() == "Interactive Graphic" or \
				text.strip() == "Download" or \
				text.strip() == "Audio Full Text" or \
				text.strip() == "Key Clinical Points" or \
				text.strip() == "Poll" or \
				text.startswith("Comments open through") or \
				text.startswith("Citing Article") or \
				text.startswith("Option 1") or \
				text.startswith("Option 2") or \
				re.match("^[0-9]+ Reference", text) or \
				re.match("^[0-9]+ Citing Article", text) or \
				re.match("^[0-9]+ Comment", text):
				keep[i] = False
			# Remove sign-ups
			elif text.startswith("Sign up for"):
				keep[i] = False
			elif text.strip() == "":
				keep[i] = False

			######################
			# Remove text before #
			######################
			if article_type == "jw.na":
				for j in range(5): # Remove first 5 lines
					keep[j] = False
			elif article_type == "oa": # Original Article
				if text.strip() == "Abstract":
					for j in range(i):
						keep[j] = False
			elif article_type == "cpc": # Case Records
				if text.strip() == "Presentation of Case":
					for j in range(i):
						keep[j] = False

			#####################
			# Remove text after #
			#####################
			if article_type == "jw.na":
				if text.startswith("EDITOR DISCLOSURES AT TIME OF PUBLICATION") or \
					text.startswith("CITATION"):
					for j in range(i, len(keep)):
						keep[j] = False
					break

			# Original Article
			# Review Article
			# Case Records
			# Perspective
			# Editorial
			# Clinical Problem Solving
			# Clinical Implications of Basic Research
			# Special report
			# Clinical decision
			# Special article
			# Clinical Therapeutics
			# Health policy report
			# Clinical Practice
			# Medicine and Society
			elif article_type in ["oa", "ra", "cpc", "p", "e", "ms",\
				"cps", "cibr", "sr", "clde", "sa", "ct", "hpr", "cp"]: 
				if text.startswith("Disclosure"):
					for j in range(i, len(keep)):
						keep[j] = False
					break

	# Output to disk
	article_filt = []
	for a, k in zip(article, keep):
		if k == True:
			article_filt.append(a)

	return article_filt


def main():
	meta = read_article_urls(url_dir)
	meta = meta[meta["year"] != 2020] # Remove year 2020

	for index, row in meta.iterrows():
		year = row["year"]
		month = row["month"]
		article_id = row["id"]
		article_type = re.sub("[0-9%]+", "", article_id)

		for lang in ["zh", "en"]:
			in_fn = f"{article_dir}/{year}/{month:02}/{article_id}.full.{lang}"
			print(f"path: {in_fn}")
			article = read_article(in_fn)
			article = stitch(article, lang)
			article = filter(article, article_type, lang)

			out_fn = in_fn.replace(".full.", ".pp2.")
			with open(out_fn, "w") as f: 
				for line in article:
					f.write(line + "\n")


if __name__ == "__main__":
	main()