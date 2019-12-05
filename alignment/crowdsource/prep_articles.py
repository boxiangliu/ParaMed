#!/usr/bin/env python
import os

in_dir = "/mnt/scratch/boxiang/projects/med_translation/"\
	"processed_data/preprocess/sentences/"
out_dir = "/mnt/scratch/boxiang/projects/med_translation/"\
	"processed_data/alignment/crowdsource/prep_articles/"
os.makedirs(out_dir, exist_ok=True)

articles = ["鼻咽癌的吉西他滨联合顺铂诱导化疗",
	"饮水可对饮用含糖饮料产生多大程度的对抗作用",
	"帕妥珠单抗和曲妥珠单抗辅助治疗早期HER2阳性乳腺癌",
	"转移性去势抵抗性前列腺癌的恩杂鲁胺耐药",
	"婴儿B群链球菌疾病预防指南更新",
	"黑种人理发店可帮助顾客降血压",
	"内科患者应用阿哌沙班和依诺肝素预防血栓形成的比较",
	"尼拉帕尼用于铂类敏感型复发性卵巢癌的维持治疗",
	"膀胱切除术的最佳手术方法：开放式手术与机器人辅助手术的比较",
	"1型糖尿病患者胰岛素治疗中加用sotagliflozin的效果",
	"HIV相关癌症和疾病",
	"2017年慢性阻塞性肺疾病诊断和治疗的GOLD指南"]

def add_line_num(in_fn, out_fn):
	with open(in_fn, "r") as fin, open(out_fn, "w+") as fout:
		num = 0
		for line in fin:
			num += 1
			line = f"【{num}】\t{line}\n"
			fout.write(line)


for article in articles:
	print(article, flush=True)
	en_in = f"{in_dir}/{article}.en"
	zh_in = f"{in_dir}/{article}.zh"

	en_out = f"{out_dir}/{article}.en"
	zh_out = f"{out_dir}/{article}.zh"

	add_line_num(en_in, en_out)
	add_line_num(zh_in, zh_out)

