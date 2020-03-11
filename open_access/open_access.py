import glob
import os
in_dir = "../processed_data/preprocess/truecase/"

train_en_fn = "../processed_data/split_data/split_train_test/nejm.train.en"
train_zh_fn = "../processed_data/split_data/split_train_test/nejm.train.zh"

os.makedirs("../processed_data/open_access/open_access/", exist_ok=True)
open_access_en_fn = "../processed_data/open_access/open_access/nejm.train.en"
open_access_zh_fn = "../processed_data/open_access/open_access/nejm.train.zh"

open_access = set()

for fn in glob.glob(f"{in_dir}/jw*.en"):
	print(fn)
	with open(fn, "r") as f:
		for line in f:
			open_access.add(line)

for fn in glob.glob(f"{in_dir}/oa*.en"):
	print(fn)
	with open(fn, "r") as f:
		for line in f:
			open_access.add(line)

with open(train_en_fn, "r") as fen_in, open(train_zh_fn, "r") as fzh_in, \
	open(open_access_en_fn, "w") as fen_out, open(open_access_zh_fn, "w") as fzh_out:
	while True:
		en = fen_in.readline()
		zh = fzh_in.readline()
		if en == "": break
		if en in open_access:
			fen_out.write(en)
			fzh_out.write(zh)

