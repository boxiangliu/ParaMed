#!/usr/bin/env python
from collections import defaultdict
import pandas as pd
import os

wd = "../processed_data/preprocess/alignment/"
align_fn = f"{wd}/align_validation_zh_en.txt"
src_fn = f"{wd}/nejm_valid.zh"
tgt_fn = f"{wd}/nejm_valid.en"
out_dir = "../processed_data/publication/tables/tab1/tab1/"
os.makedirs(out_dir, exist_ok=True)

def read_sents(fn):
	df = pd.read_table(fn, sep="\t", names=["doc","sent","text"])
	return df


def parse_align_string(s):
	if s == "omitted":
		align = []
	elif "," in s:
		align = [int(x) for x in s.split(",")]
	else:
		align = [int(s)]
	return align


def read_align(fn):
	proto_df = defaultdict(list)
	with open(fn, "r") as fin:
		for line in fin:
			split_line = line.split("\t")
			doc = split_line[0]
			alignment = split_line[1]
			src_no, tgt_no = alignment.split(" <=> ")
			src_list = parse_align_string(src_no)
			tgt_list = parse_align_string(tgt_no)
			align_type = f"{len(src_list)} - {len(tgt_list)}"
			proto_df["doc"].append(doc)
			proto_df["zh"].append(src_list)
			proto_df["en"].append(tgt_list)
			proto_df["type"].append(align_type)
	df = pd.DataFrame(proto_df)
	return df


def merge_align_n_text(align, zh, en):
	proto_df = defaultdict(list)
	for i in range(align.shape[0]):
		
		doc = align["doc"].iloc[i]
		zh_sents = align["zh"].iloc[i]
		en_sents = align["en"].iloc[i]
		
		zh_text = en_text = ""

		for sent in zh_sents:
			zh_text += zh[(zh["doc"] == doc) & (zh["sent"] == sent)]\
				["text"].item()
		for sent in en_sents:
			en_text += en[(en["doc"] == doc) & (en["sent"] == sent)]\
				["text"].item()
		
		proto_df["zh_text"].append(zh_text)
		proto_df["en_text"].append(en_text)

	align["zh_text"] = proto_df["zh_text"]
	align["en_text"] = proto_df["en_text"]

	return align


def smrize_alignment(align):
	df = align.groupby("type").\
		agg(Count=pd.NamedAgg("doc","count")).\
		reset_index()
	s = sum(df["Count"])
	df["Percent"] = ["{:.02f}%".format(x/s*100) for x in df["Count"]]
	return df


def get_latex_table():
	pass

zh = read_sents(src_fn)
en = read_sents(tgt_fn)
align = read_align(align_fn)
align = merge_align_n_text(align, zh, en)
smry = smrize_alignment(align)
with open(f"{out_dir}/count.tex", "w+") as f:
	smry.to_latex(f, index=False)

align_type = ["0 - 1", "1 - 0", "1 - 1", "1 - 2", "2 - 1", "2 - 2", "2 - 3"]
zh_example = ["", "主要的安全结局是出血。", 
"加用吉西他滨联合顺铂诱导化疗在2期试验中显示出很有前景的疗效。",
"在铂类敏感的复发性卵巢癌患者中，无论存在或不存在gBRCA突变或HRD状态，与接受安慰剂的患者相比，接受尼拉帕尼治疗的患者的中位无进展生存期显著延长，存在中度骨髓毒性（本研究由Tesaro公司资助；在ClinicalTrials.gov注册号为NCT01847274）。",
"sotagliflozin是一种口服钠-葡萄糖协同转运蛋白-1和2的抑制剂。我们评价了在1型糖尿病患者中联用胰岛素和sotagliflozin的安全性和疗效。",
"与安慰剂组相比，腹泻在帕妥珠单抗组较为常见（由霍夫曼-罗氏/基因泰克[Hoffmann-La Roche/Genentech]资助。APHINITY在ClinicalTrials.gov注册号为NCT01358877）。",
"这些患者被包括在非-gBRCA HRD-阳性亚组中（同源重组率降低被发现可引起低效的DNA修复。更多细节在补充附录的方法部分提供）。"]
en_example = ["No other potential conflict of interest relevant to this article was reported.","",
"Additional gemcitabine and cisplatin induction chemotherapy has shown promising efficacy in phase 2 trials.",
"Among patients with platinum-sensitive, recurrent ovarian cancer, the median duration of progression-free survival was significantly longer among those receiving niraparib than among those receiving placebo, regardless of the presence or absence of gBRCA mutations or HRD status, with moderate bone marrow toxicity. (Funded by Tesaro; ClinicalTrials.gov number, NCT01847274.)",
"We evaluated the safety and efficacy of sotagliflozin, an oral inhibitor of sodium–glucose cotransporters 1 and 2, in combination with insulin treatment in patients with type 1 diabetes.",
"Diarrhea was more common with pertuzumab than with placebo. (Funded by F. Hoffmann–La Roche/Genentech; APHINITY ClinicalTrials.gov number, NCT01358877.)",
"Such patients were included in the non-gBRCA HRD-positive subgroup. (Decreased rates of homologous recombination have been found to cause inefficient DNA repair. Additional details are provided in the Methods section in the Supplementary Appendix.)"]
example = pd.DataFrame({"type":align_type, "zh": zh_example, "en": en_example})

with open(f"{out_dir}/examples.tex", "w+") as f:
	example.to_latex(f, index=False)

