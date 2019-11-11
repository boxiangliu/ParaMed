from argparse import Namespace
import pandas as pd
pd.options.display.max_columns = 99
from collections import defaultdict
import ipdb

args = Namespace(align_fn="../data/wmt19_biomed_modified/align_validation_zh_en.txt",
			  en_fn="../data/wmt19_biomed_modified/medline_zh2en_en.txt",
			  zh_fn="../data/wmt19_biomed_modified/medline_zh2en_zh.txt")

def read_data(args):

	align = pd.read_table(args.align_fn, names=["pmid", "doc", "align", "status"])
	align["zh"] = [x.split(" <=> ")[0] for x in align["align"]]
	align["en"] = [x.split(" <=> ")[1] for x in align["align"]]
	en = pd.read_table(args.en_fn, names=["doc", "sent_id", "sent"])
	zh = pd.read_table(args.zh_fn, names=["doc", "sent_id", "sent"])

	return align, en, zh


def align_en_zh(docs, align, en, zh):
	alignment = defaultdict(list)

	for doc in docs:
		e = en[en.doc == doc]
		z = zh[zh.doc == doc]
		a = align[align.doc == doc]
		pmid = a.pmid.unique().item()
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
			alignment["pmid"].append(pmid)
			alignment["status"].append(status)
			alignment["align_zh"].append(i)
			alignment["align_en"].append(j)
			alignment["zh"].append(zh_sent)
			alignment["en"].append(en_sent)

	alignment = pd.DataFrame(alignment)
	return alignment

def main():
	align, en, zh = read_data(args)
	docs = align.doc.unique()
	alignment = align_en_zh(docs, align, en, zh)