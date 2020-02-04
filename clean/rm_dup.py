#!/usr/bin/env python
# The output of Bifixer has two additional columns. 
# The 5th column is a hash of the sentence pair
# The 6th column is a score (higher = better)
# For all sentences with the same hash, 
# this script keeps one with the highest score. 
import sys

in_fn = sys.argv[1]
out_fn = sys.argv[2]

# in_fn = "/mnt/scratch/boxiang/projects/med_translation/"\
# "processed_data/clean/input/nejm.bifixer.all"
# out_fn = "/mnt/scratch/boxiang/projects/med_translation/"\
# "processed_data/clean/input/nejm.rm_dup.all"
print("Sifting through all sentences...")
with open(in_fn, "r") as f:
	keep_dict = dict()
	remove_set = set()
	for i, line in enumerate(f):
		split_line = line.strip().split("\t")
		zh = split_line[2]
		en = split_line[3]
		hash_ = split_line[4]
		score = float(split_line[5])

		# If hash not in keep_dict, add it.
		if hash_ not in keep_dict:
			keep_dict[hash_] = (score, i, zh, en)

		# If hash is in keep_dict, compare with the 
		# existing score
		else:
			if keep_dict[hash_][0] < score:
				remove_set.add(keep_dict[hash_])
				keep_dict[hash_] = (score, i, zh, en)
			else:
				remove_set.add((score, i, zh, en))

print("Saving sentences with highest scores.")
lines_to_keep = set()
for k, v in keep_dict.items():
	lines_to_keep.add(v[1])


with open(in_fn, "r") as fin, open(out_fn, "w") as fout:
	for i, line in enumerate(fin):
		if i in lines_to_keep:
			fout.write(line)



