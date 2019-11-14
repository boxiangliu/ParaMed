import argparse 
import os
import pandas as pd
pd.options.display.max_columns = 99
pd.options.display.max_rows = 1000
import numpy as np
from collections import defaultdict
import ipdb
from sklearn.metrics import precision_score,\
	recall_score

parser = argparse.ArgumentParser(description="Generate precision-recall "\
	"table for sentence alignments.")
parser.add_argument("--align_fn", type=str, help="Path to ground-truth "\
	"alignment file.")
parser.add_argument("--en_fn", type=str, help="Path to English sentences.")
parser.add_argument("--zh_fn", type=str, help="Path to Chinese sentences.")
parser.add_argument("--pred_fn", type=str, help="Path to prediction sentence.")
parser.add_argument("--out_fn", type=str, help="Path to output precision "\
	"recall table.")
args = parser.parse_args()
os.makedirs(os.path.dirname(args.out_fn), exist_ok=True)

# Example
# args = Namespace(align_fn="../data/wmt19_biomed_modified/align_validation_zh_en.txt",
# 			  en_fn="../data/wmt19_biomed_modified/medline_zh2en_en.txt",
# 			  zh_fn="../data/wmt19_biomed_modified/medline_zh2en_zh.txt",
# 			  pred_fn="../data/wmt19_biomed_modified/align_bleualign_zh_en.txt",
# 			  out_fn="../processed_data/evaluation/wmt19_biomed/evaluate/bleualign.pr")


def align_en_zh(align, en, zh):

	align["zh"] = [x.split(" <=> ")[0] for x in align["align"]]
	align["en"] = [x.split(" <=> ")[1] for x in align["align"]]

	docs = align.doc.unique()
	alignment = defaultdict(list)

	for doc in docs:
		e = en[en.doc == doc]
		z = zh[zh.doc == doc]
		a = align[align.doc == doc]
		if e.shape[0] == 0 or z.shape[0] == 0: 
			continue
		
		for i, j, status in \
			zip(a["zh"], a["en"], a["status"]):

			zh_sent = ""
			en_sent = ""

			for v in i.split(","):
				if v != "omitted":
					v = int(v) - 1
					zh_sent += z["sent"].iloc[v]

			for w in j.split(","):
				if w != "omitted":
					w = int(w) - 1
					en_sent += e["sent"].iloc[w]

			alignment["doc"].append(doc)
			alignment["status"].append(status)
			alignment["align"].append("{} <=> {}".format(i,j))
			alignment["zh"].append(zh_sent)
			alignment["en"].append(en_sent)

	alignment = pd.DataFrame(alignment)
	return alignment


def read_data(args):
	en = pd.read_table(args.en_fn, names=["doc", "sent_id", "sent"])
	zh = pd.read_table(args.zh_fn, names=["doc", "sent_id", "sent"])

	align = pd.read_table(args.align_fn, names=["pmid", "doc", "align", "status"])
	align = align_en_zh(align, en, zh)
	return align, en, zh


def copy_validation_align(row):
	if row["status_val"] is not np.NaN:
		return row["align"]
	else:
		return np.NaN

def copy_pred_align(row):
	if row["status_pred"] is not np.NaN \
		or "omitted" in row["align"]:
		return row["align"]
	else:
		return np.NaN

def align_type(x):
	out = []
	for i in x:
		if i is np.NaN:
			out.append(np.NaN)
		else:
			src, tgt = i.split(" <=> ")
			if src == "omitted":
				src_len = 0
			else:
				src_len = len(src.split(","))

			if tgt == "omitted":
				tgt_len = 0
			else:
				tgt_len = len(tgt.split(","))
			min_len = min(src_len, tgt_len)
			max_len = max(src_len, tgt_len)
			out.append("{} - {}".format(min_len, max_len))
	return out

def main():
	align, en, zh = read_data(args)
	pred = pd.read_table(args.pred_fn, names=["doc", "align","status", "zh", "en"])
	merged = pd.merge(align[["doc", "align", "status"]], 
		pred[["doc", "align", "status"]], 
		on=["doc", "align"], how="outer", suffixes=("_val", "_pred")).\
		sort_values(["doc", "align"])

	merged["align_val"] = merged.apply(lambda x: copy_validation_align(x), axis=1)
	merged["align_pred"] = merged.apply(lambda x: copy_pred_align(x), axis=1)
	merged["type_val"] = align_type(merged["align_val"])
	merged["type_pred"] = align_type(merged["align_pred"])

	pr_table = defaultdict(list)
	for atype in merged["type_val"].unique():
		if atype is np.NaN:
			continue

		truths = merged.assign(val=lambda x: x["type_val"].eq(atype),
				  ble=lambda x: x["type_pred"].eq(atype))
		precision = precision_score(truths["val"], truths["ble"])
		recall = recall_score(truths["val"], truths["ble"])
		pr_table["type"].append(atype)
		pr_table["precision"].append(precision)
		pr_table["recall"].append(recall)
	pr_table = pd.DataFrame(pr_table)
	pr_table.to_csv(args.out_fn, sep="\t", index=False)

if __name__ == "__main__":
	main()
