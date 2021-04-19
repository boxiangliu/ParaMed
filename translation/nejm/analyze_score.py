from collections import defaultdict
import pandas as pd

nejm_zh2en = "../processed_data/translation/nejm/finetune/test/nejm.93303.zh2en.log"
wmt_zh2en = "../processed_data/translation/nejm/finetune/test/wmt18.zh2en.log"

nejm_en2zh = "../processed_data/translation/nejm/finetune/test/nejm.93303.en2zh.log"
wmt_en2zh = "../processed_data/translation/nejm/finetune/test/wmt18.en2zh.log"

def read_openNMT_translation_log(fn, direction):
	assert direction in ["zh2en", "en2zh"], \
		"direction must be zh2en or en2zh."
	container = defaultdict(list)

	with open(fn, "r") as f:
		for i, line in enumerate(f):

			if line.startswith("SENT"):
				if direction == "zh2en":
					zh = line.strip().split(":")[1]
					zh = zh.replace("['", "").replace("']","").\
						replace("', '", "").replace("@@", "")
					container["zh"].append(zh)
				else:
					en = line.strip().split(":")[1]
					en = en.replace("['", "").replace("']","").\
						replace("', '", " ").replace("@@ ", "")
					container["en"].append(en)
				container["index"].append(i)
			
			elif line.startswith("PRED SCORE"):
				score = float(line.strip().split(":")[1].strip())
				container["score"].append(score)

			elif line.startswith("PRED AVG SCORE"):
				pass

			elif line.startswith("PRED"):
				text = line.strip().split(":")[1]
				text = text.replace("@@ ", "")
				if direction == "zh2en":
					container["en"].append(text)
				else:
					container["zh"].append(text)
			else:
				pass
	return pd.DataFrame(container)


nejm = read_openNMT_translation_log(nejm_zh2en, direction="zh2en")
wmt = read_openNMT_translation_log(wmt_zh2en, direction="zh2en")
merged = pd.merge(nejm, wmt, on="index", suffixes=["_nejm", "_wmt"])
merged["score_diff"] = merged.apply(lambda x: x["score_nejm"] - x["score_wmt"], axis=1)
merged = merged.sort_values("score_diff", ascending=False)


# In [92]: merged.iloc[8]["zh_nejm"]                                                                                                
# Out[92]: ' 患者接受铂类-紫杉类药物化疗+贝伐珠单抗一线治疗后,本研究要求其不能有病变迹象,或者在治疗后达到临床完全或部分缓解(定义参见表1).'

# In [93]: merged.iloc[8]["en_nejm"]                                                                                                
# Out[93]: ' patients were required to have no evidence of disease or to have a clinical complete or partial response after treatment after first @-@ line platinum @-@ taxane chemotherapy plus bevacizumab ( as defined in Table 1 ) .'

# In [94]: merged.iloc[8]["en_wmt"]                                                                                                 
# Out[94]: ' after Pt @-@ Pseudophyllus drug chemotherapy + Bavaris mono @-@ repellent first @-@ line treatment , the study required that the patient should not show signs of lesion or complete or partial clinical relief after treatment ( see table 1 for definition ) .'



nejm = read_openNMT_translation_log(nejm_en2zh, direction="en2zh")
wmt = read_openNMT_translation_log(wmt_en2zh, direction="en2zh")
merged = pd.merge(nejm, wmt, on="index", suffixes=["_nejm", "_wmt"])
merged["score_diff"] = merged.apply(lambda x: x["score_nejm"] - x["score_wmt"], axis=1)
merged = merged.sort_values("score_diff", ascending=False)

merged.iloc[20]["en_nejm"]
merged.iloc[20]["zh_nejm"]
merged.iloc[20]["zh_wmt"]