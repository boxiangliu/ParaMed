from argparse import Namespace
import pandas as pd
pd.options.display.max_columns = 99
from collections import defaultdict
import ipdb

args = Namespace(align_fn="../data/wmt19_biomed/align_validation_zh_en.txt",
			  en_fn="../data/wmt19_biomed/medline_zh2en_en.txt",
			  zh_fn="../data/wmt19_biomed/medline_zh2en_zh.txt",
			  mapdocs_fn="../data/wmt19_biomed/mapdocs_zh_en.txt")

def read_data(args):

	align = pd.read_table(args.align_fn, names=["pmid", "align", "status"])
	align["zh"] = [x.split(" <=> ")[0] for x in align["align"]]
	align["en"] = [x.split(" <=> ")[1] for x in align["align"]]
	en = pd.read_table(args.en_fn, names=["doc", "sent_id", "sent"])
	zh = pd.read_table(args.zh_fn, names=["doc", "sent_id", "sent"])
	mapdocs = pd.read_table(args.mapdocs_fn, names=["doc", "pmid"])

	en = pd.merge(en, mapdocs, on="doc", sort=False)
	zh = pd.merge(zh, mapdocs, on="doc", sort=False)

	return align, en, zh, mapdocs


def align_en_zh(pmids, align, en, zh):
	alignment = defaultdict(list)

	for pmid in pmids:
		e = en[en.pmid == pmid]
		z = zh[zh.pmid == pmid]
		if e.shape[0] == 0 or z.shape[0] == 0: 
			continue

		a = align[align.pmid == pmid]
		for i, j, align_zh, align_en, status in \
			zip(a["zh"], a["en"], a["zh"], a["en"], a["status"]):

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

			alignment["pmid"].append(pmid)
			alignment["status"].append(status)
			alignment["align_zh"].append(align_zh)
			alignment["align_en"].append(align_en)
			alignment["zh"].append(zh_sent)
			alignment["en"].append(en_sent)

	alignment = pd.DataFrame(alignment)
	return alignment

def cleanup(alignment):
	# NO_ALIGNMENT:
	no_alignment = alignment[alignment.status == "NO_ALIGNMENT"]
	no_alignment
	alignment.iat[25, 1] = "OK"
	alignment.iloc[141,:].tolist()
	for a,b in zip(alignment[alignment.pmid == 30756538].zh.tolist(), alignment[alignment.pmid == 30756538].en.tolist()):
		print(a)
		print(b)

# doc44: removed because of incorrect alignment.
# doc1 (omitted <=> 10, NO_ALIGNMENT): changed to OK
# doc2 (2 <=> 3,4, TARGET_GREATER_SOURCE):  changed to 2,3 <=> 3,4
# doc2 (3 <=> omitted, NO_ALIGNMENT): same as above
# doc3 (3 <=> 5, TARGET_GREATER_SOURCE): changed to 3 <=> 5,6
# doc3 (4 <=> 6,7, SOURCE_GREATER_TARGET): changed to 4 <=> 7 
# doc5 (9 <=> 11,12, NO_ALIGNMENT): changed to OK
# doc6: removed, sentences not found. 
# doc7: removed, sentences not found. 
# doc8 (2 <=> 4,5,	TARGET_GREATER_SOURCE): changed to 2 <=> 4
# doc8	(3 <=> 6,7, SOURCE_GREATER_TARGET): changed to 3 <=> 5,6,7
# doc9 (1 <=> 1, SOURCE_GREATER_TARGET): removed 摘要 from source side.
# doc11 (1 <=> 1, SOURCE_GREATER_TARGET): removed 目的：
# doc12: removed, sentence not found.
# doc15: removed, sentence not found.
# doc16 (3 <=> 3,4,5, TARGET_GREATER_SOURCE): 3 <=> 3,4
# doc16 (4 <=> 6, SOURCE_GREATER_TARGET): 4 <=> 5,6
# doc18: removed, sentences not found.
# doc20 (4 <=> 5, SOURCE_GREATER_TARGET): changed to OK
# doc22, 23, 24, 27, 29: removed, sentences not found.
# doc30 (4 <=> 4, SOURCE_GREATER_TARGET): 4 <=> 4, 5
# doc34: removed, sentence not found.
# doc35 (1 <=> 1): removed 目的：
# doc35	(omitted <=> 3, NO_ALIGNMENT): changed to OK
# doc35 (4 <=> 5, SOURCE_GREATER_TARGET): 4 <=> 5,6
# doc35 (5 <=> 6,7,8, TARGET_GREATER_SOURCE): 5 <=> 7,8
# doc36	(1 <=> 1,2, TARGET_GREATER_SOURCE): changed to OK
# doc37: removed, sentences not found.
# doc38 (1 <=> 1): removed 目的：
# doc46: removed, sentences not found.
# doc47, 3 <=> 4,5,6,7, OVERLAP and doc47. 4 <=> 8, NO_ALIGNMENT: combined into 3,4 <=> 4,5,6,7,8.
# doc48 (3 <=> 3,4,5,6, SOURCE_GREATER_TARGET): 3 <=> 3,4,5,6,7 
# doc48 (omitted <=> 7): see above
# doc49 (1 <=> 1): removed 目的：
# dpc53: removed, sentences not found.
# doc55: removed, sentences not found.
# doc57: removed, sentences not found.
# doc58	(8 <=> 11, SOURCE_GREATER_TARGET): changed to OK
# doc60 (8 <=> 9, SOURCE_GREATER_TARGET): changed to OK
# doc61: removed, sentences not found.
# doc67, 68, 69, 78, 80: removed, sentences not found. 
# doc82 (3 <=> 5, SOURCE_GREATER_TARGET): changed to OK
# doc83, 85: removed, sentences not found
# doc90 (2 <=> 2, SOURCE_GREATER_TARGET): changed to TARGET_GREATER_SOURCE
# doc93 (1 <=> 2, SOURCE_GREATER_TARGET) and doc93 (omitted <=> 1, NO_ALIGNMENT): combined
def main():
	align, en, zh, mapdocs = read_data(args)
	pmids = mapdocs.pmid.unique().tolist()
	pmids.remove(30648242)
	alignment = align_en_zh(pmids, align, en, zh)