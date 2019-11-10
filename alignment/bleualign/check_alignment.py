import glob
from utils.utils import Article
import os
from collections import Counter
import ipdb

align_dir = "/mnt/home/boxiang/projects/med_translation/processed_data/alignment/bleualign/align/"
article = "黏膜炎症是否增加溃疡性结肠炎患者的肿瘤发生风险"
src = "{}/{}.align-s".format(align_dir, article)
tgt = "{}/{}.align-t".format(align_dir, article)

src_list = glob.glob("{}/*.align-s".format(align_dir))
assert len(src_list) == len(tgt_list), \
	"Source and target should be same length."

def counter_is_uniq(article):
	number = [p.number for p in article.paragraphs \
		if p.number != Counter()]
	prefix = []
	for n in number:
		if n not in prefix:
			prefix.append(n)
		else:
			print("Duplicate entry: {}".format(n))
			return False
	assert prefix == number
	return True

def get_counter_stat(art1, art2):
	counter1 = [p.number for p in art1.paragraphs \
		if p.number != Counter()]
	counter2 = [p.number for p in art2.paragraphs \
		if p.number != Counter()]
	ipdb.set_trace()
	# assert len(counter1) == len(counter2), \
		# "Number of paragrahs are different."
	length = len(counter2)
	num_diff = 0
	if counter1 != counter2:
		for c2 in counter2:
			if c2 not in counter1:
				num_diff += 1
	return length - num_diff, length


total_sent = num_diff = 0
diff_sent = []
for src in src_list:
	tgt = src.replace("-s", "-t")
	zh = Article(path=src, lang="zh")
	en = Article(path=tgt, lang="en")

	for s1, s2 in zip(zh.paragraphs, en.paragraphs):
		total_sent += 1
		if s1.number != s2.number:
			num_diff +=1
			diff_sent.append([src, tgt, s1, s2])

# total_sent = 126041
# num_diff = 16196
