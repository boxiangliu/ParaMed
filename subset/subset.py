#!/usr/bin/env python
# Subset the NEJM corpus to 4k, 8k, 16k, 32k,
# 64k sentence pairs.

import os
from collections import defaultdict

in_dir = "../processed_data/split_data/split_train_test/"
src_fn = f"{in_dir}/train.zh"
tgt_fn = f"{in_dir}/train.en"

out_dir = "../processed_data/subset/subset/"
os.makedirs(out_dir, exist_ok=True)

with open(src_fn, "r") as f:
	N = len(f.readlines())
subset = [4000, 8000, 16000, 32000, 64000, N]

# Open file handles:
out_fh = defaultdict(dict)
for n in subset:
	for side in ["zh", "en"]:
		fn = f"{out_dir}/nejm.train.{n}.{side}"
		out_fh[n][side] = open(fn, "w")


with open(src_fn, "r") as fsrc, open(tgt_fn, "r") as ftgt:
	for i in range(N):
		src = next(fsrc)
		tgt = next(ftgt)

		for n in subset:
			if i < n:
				if i % 4000 == 0:
					print(f"##### Line {i} #####.")
					print(f"Writing to {out_dir}/nejm.train.{n}.{side}.")
				out_fh[n]["zh"].write(src)
				out_fh[n]["en"].write(tgt)


# Close file handles:
for n in subset:
	for side in ["zh", "en"]:
		out_fh[n][side].close()
