import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')
import seaborn as sns
import pandas as pd
import argparse 
from glob import glob
import os

parser = argparse.ArgumentParser(description="Visualize precision and recall"\
	"of sentence alignment.")
parser.add_argument("--in_dir", type=str, 
	help="Path to precision recall tables.",
	default="../processed_data/evaluation/nejm/evaluate/")
parser.add_argument("--out_dir", type=str, help="Path to output directory.",
	default="../processed_data/evaluation/nejm/evaluate/")
args = parser.parse_args()

in_dir = args.in_dir
out_dir = args.out_dir

def get_f1(precision, recall):
	if precision + recall > 0:
		f1 = 2*precision*recall/(precision + recall)
	else:
		f1 = 0
	return f1

pr_files = glob(f"{in_dir}/*.pr")

container = []
for file in pr_files:
	pr = pd.read_table(file)
	aligner = os.path.basename(file).replace(".pr","")
	pr["aligner"] = aligner
	container.append(pr)

pr = pd.concat(container)
pr["f1"] = pr.apply(axis=1, func=lambda x: get_f1(x["precision"],x["recall"]))
pr = pd.melt(pr, id_vars=["type", "aligner"])

p1 = sns.barplot(data=pr[pr["type"] == "1 - 1"], 
	x="aligner", y="value", hue="variable")

p1.figure.savefig(f"{out_dir}/pr.png")