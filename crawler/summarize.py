import pandas as pd
from collections import defaultdict

def count_articles(container):
	proto_df = defaultdict(list)
	for year, months in container.items():
		for month, articles in months.items():
			proto_df["year"].append(year)
			proto_df["month"].append(month)
			proto_df["articles"].append(len(articles))
	df = pd.DataFrame(proto_df)
	df.sort_values(by=["year", "month"], inplace=True)
	return df 

df = count_articles(container)
df.articles.sum()