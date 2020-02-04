import os
import sys 
sys.path.append(".")
from collections import defaultdict
from utils.utils import read_article_urls

url_dir = "../processed_data/crawler/nejm/urls/"
align_dir = "../processed_data/clean/clean/"
out_dir = "../processed_data/split_data/split_train_test/"
os.makedirs(out_dir, exist_ok=True)

def save_aligned_sent(prefix, docs, align):
	with open(f"{prefix}.zh", "w") as fzh, \
		open(f"{prefix}.en", "w") as fen:
		for i in docs:
			for sent in align[align["id"] == i]["zh"]:
				fzh.write(sent.strip() + "\n")
			for sent in align[align["id"] == i]["en"]:
				fen.write(sent.strip() + "\n")


print("Reading articles...")
article_urls = read_article_urls(url_dir)
df = defaultdict(list)
with open(f"{align_dir}/all.rm_dup.txt", "r") as f:
	for line in f:
		split_line = line.split("\t")
		df["id"].append(split_line[0])
		df["sent"].append(split_line[1])
		df["zh"].append(split_line[2])
		df["en"].append(split_line[3])
align = pd.DataFrame(df)


print("Counting number of sentences in each article...")
num_sent = align.groupby("id").agg(num_sent=pd.NamedAgg("id","count"))


print("Sorting article by year and month...")
num_sent = pd.merge(article_urls[["year", "month", "id"]], num_sent, on="id")
num_sent = num_sent.sort_values(["year", "month"], ascending=False)


print("Selecting sentences for the test set...")
num_sent["cumsum"] = num_sent["num_sent"].cumsum()
test_sent = num_sent[num_sent["cumsum"] >= 2000]["cumsum"].iloc[0]
test_docs = num_sent[num_sent["cumsum"] <= test_sent]["id"]


print(f"Writing {test_sent} test sentences...")
save_aligned_sent(f"{out_dir}/test", test_docs, align)


print("Selecting sentences for the dev set...")
dev_sent = num_sent[num_sent["cumsum"] >= 2000 + test_sent]["cumsum"].iloc[0]
dev_docs = num_sent[(num_sent["cumsum"] <= dev_sent) & (num_sent["cumsum"] > test_sent)]["id"]


print(f"Writing {dev_sent-test_sent} dev sentences...")
save_aligned_sent(f"{out_dir}/dev", dev_docs, align)


print(f"Writing training sentences...")
train_docs = num_sent[num_sent["cumsum"] > dev_sent]["id"]
save_aligned_sent(f"{out_dir}/train", train_docs, align)