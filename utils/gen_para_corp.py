import argparse
import pandas as pd
import os
from collections import defaultdict

parser = argparse.ArgumentParser(description="Convert alignment file "\
	"into parallel corpora.")
parser.add_argument("--align_fn", type=str, help="Path to ground-truth "\
	"alignment file.")
parser.add_argument("--zh_fn", type=str, help="Path to English sentences.")
parser.add_argument("--en_fn", type=str, help="Path to Chinese sentences.")
parser.add_argument("--out_fn", type=str, help="Path to output directory.")
args = parser.parse_args()
os.makedirs(os.path.dirname(args.out_fn), exist_ok=True)


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
			add_to_alignment = True

			for v in i.split(","):
				if v != "omitted":
					v = int(v) - 1
					zh_sent += z["sent"].iloc[v]
				else:
					add_to_alignment = False

			for w in j.split(","):
				if w != "omitted":
					w = int(w) - 1
					en_sent += e["sent"].iloc[w]
				else:
					add_to_alignment = False

			if add_to_alignment:
				alignment["doc"].append(doc)
				alignment["align"].append("{} <=> {}".format(i,j))
				alignment["status"].append(status)
				alignment["zh"].append(zh_sent)
				alignment["en"].append(en_sent)

	alignment = pd.DataFrame(alignment)
	return alignment


def read_data(args):
	shape_getter = pd.read_table(args.align_fn, nrows=10)
	ncol = shape_getter.shape[1]
	print(f"{ncol} columns detected in alignment file.")

	if ncol == 3:
		align = pd.read_table(args.align_fn, names=["doc", "align", "status"])
	elif ncol == 4:
		align = pd.read_table(args.align_fn, names=["pmid", "doc", "align", "status"])
	else:
		raise ValueError(f"Column = {ncol} has not been implemented.")
	
	if args.en_fn is not None and args.zh_fn is not None:

		en = pd.read_table(args.en_fn, names=["doc", "sent_id", "sent"])
		zh = pd.read_table(args.zh_fn, names=["doc", "sent_id", "sent"])
		align = align_en_zh(align, en, zh)

	else:
		en = None
		zh = None
	
	return align, en, zh


def main(args):
	align, _, _ = read_data(args)
	for lang in ["zh", "en"]:
		with open(f"{args.out_fn}.{lang}", "w+") as f:
			for sent in align[lang]:
				f.write(sent + "\n")

if __name__ == "__main__":
	main(args)