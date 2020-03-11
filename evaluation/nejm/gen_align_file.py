import re
import warnings
import argparse

parser = argparse.ArgumentParser(description="Generate alignment between "\
	"source and target in the form of src <=> tgt.")
parser.add_argument("--src_fn", type=str, help="Path to source file.")
parser.add_argument("--tgt_fn", type=str, help="Path to target file.")
parser.add_argument("--out_fn", type=str, help="Path to alignment file.")
args = parser.parse_args()
src_fn = args.src_fn
tgt_fn = args.tgt_fn
out_fn = args.out_fn

# Examples:
# src_fn = "../processed_data/evaluation/nejm/align/hunalign/align/-0.60/align.zh"
# tgt_fn = "../processed_data/evaluation/nejm/align/hunalign/align/-0.60/align.en"
# out_fn = "test.txt"


def extract_markers(sent):
	sent = sent.strip()

	markers = re.findall("\|\s{0,1}doc[0-9]+,[0-9]+", sent)
	for marker in markers:
		sent = sent.replace(marker, "")

	doc_ids = set([x.split(",")[0].replace("|","").strip() for x in markers])
	sent_ids = [x.split(",")[1] for x in markers]
	
	if len(doc_ids) == 1:
		doc_ids = doc_ids.pop()
	elif len(doc_ids) == 0:
		warnings.warn("Doc is empty")
		doc_ids = ""
	else:
		warnings.warn("Doc should be unique.")
		print(doc_ids)
		doc_ids = ",".join(list(doc_ids))

	sent_ids = ",".join(sent_ids)
	return sent, doc_ids, sent_ids


with open(src_fn, "r") as f1, open(tgt_fn, "r") as f2, \
	open(out_fn, "w+") as fout:
	n = 0
	for src_sent, tgt_sent in zip(f1, f2):
		n += 1
		src_sent, src_doc_ids, src_sent_ids = extract_markers(src_sent)
		tgt_sent, tgt_doc_ids, tgt_sent_ids = extract_markers(tgt_sent)
		if src_doc_ids == "" or tgt_doc_ids == "":
			print("Found empty doc.")
		elif src_doc_ids != tgt_doc_ids:
			warnings.warn("Source doc ({}) and target doc ({}) "\
				"should be identical.".format(src_doc_ids, tgt_doc_ids))
			fout.write("{},{}\t{} <=> {}\t{}\t{}\t{}\n".format(src_doc_ids,
				tgt_doc_ids, src_sent_ids, tgt_sent_ids, "AUTO", src_sent, 
				tgt_sent))
		else:
			fout.write("{}\t{} <=> {}\t{}\t{}\t{}\n".format(src_doc_ids,
				src_sent_ids, tgt_sent_ids, "AUTO", src_sent, tgt_sent))


