import sys 
sys.path.append(".")
from utils.utils import read_article_urls

url_dir = "../processed_data/crawler/nejm/urls/"
align_dir = "../processed_data/alignment/moore/align/"

def get_article_length(in_dir, article_urls, status):
	for index, row in article_urls.iterrows():
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


article_urls = read_article_urls(url_dir)

article_urls.sort_values(["year","month"])
article_urls