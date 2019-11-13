import re
import warnings
src_fn = "../data/wmt19_biomed_modified/align.tok.mark-s"
tgt_fn = "../data/wmt19_biomed_modified/align.tok.mark-t"
out_fn = "../data/wmt19_biomed_modified/align_bleualign_zh_en.txt"

def extract_markers(sent):
	sent = sent.strip()

	markers = re.findall("\|doc[0-9]{1,2},[0-9]{1,2}", sent)
	for marker in markers:
		sent = sent.replace(marker, "")

	doc_ids = set([x.split(",")[0].replace("|","") for x in markers])
	sent_ids = [x.split(",")[1] for x in markers]
	
	if len(doc_ids) == 1:
		doc_ids = doc_ids.pop()
	else:
		warnings.warn("Doc should be unique.")
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

		if src_doc_ids != tgt_doc_ids:
			warnings.warn("Source doc ({}) and target doc ({}) "\
				"should be identical.".format(src_doc_ids, tgt_doc_ids))
			

		fout.write("{}\t{} <=> {}\t{}\t{}\t{}\n".format(src_doc_ids,
			src_sent_ids, tgt_sent_ids, "AUTO", src_sent, tgt_sent))


