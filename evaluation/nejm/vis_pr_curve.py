import os
import glob
import pandas as pd
import matplotlib
matplotlib.use('tkagg')
import matplotlib.pyplot as plt
import seaborn as sns

in_dir = "../processed_data/evaluation/nejm/evaluate/"
out_dir = "../processed_data/evaluation/nejm/vis_pr_curve/"
os.makedirs(out_dir, exist_ok=True)

def read_precision_recall(in_dir):
	pr_files = glob.glob(f'{in_dir}/*_*.pr')
	container = []
	for fn in pr_files:
		basename = os.path.basename(fn)
		aligner = basename.split("_")[0]
		threshold = basename.split("_")[-1].replace(".pr", "")
		threshold = float(threshold)
		print(f"Aligner: {aligner}")
		print(f"Threshold: {threshold}")
		try:
			df = pd.read_table(fn)
			df["aligner"] = aligner
			df["threshold"] = threshold
			container.append(df)
		except:
			print(f"Empty (Aligner: {aligner}; Threshold: {threshold})")
	pr = pd.concat(container)
	return pr


def get_f1(precision, recall):
	if precision + recall > 0:
		f1 = 2*precision*recall/(precision + recall)
	else:
		f1 = 0
	return f1


def p1(pr):
	data = pr[pr["type"] == "1 - 1"]
	plt.figure()
	sns.scatterplot(x="precision", y="recall", hue="aligner", data=data)
	plt.tight_layout()
	plt.savefig(f"{out_dir}/pr_curve.pdf")


def p2(max_f1):
	fig, ax = plt.subplots()
	sns.barplot(x="aligner", y="max_f1", data=max_f1)
	ax.set(xlabel="Aligner", ylabel="F1")
	ax.set_xticklabels(["Microsoft", "Bleualign\nUnidirection", "Bleualign\nBidirection", "Gale-Church"])
	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)
	fig.set_size_inches(4,3)
	fig.tight_layout()
	fig.savefig(f"{out_dir}/maximum_f1.pdf")


def p3(f1_pr):
	fig, ax = plt.subplots()
	sns.barplot(x="aligner", y="value", hue="variable", data=f1_pr)
	ax.set(xlabel=None, ylabel="Precision/Recall/F1")
	ax.set_xticklabels(["Microsoft", "Uni-dir.\nBleualign", "Bi-dir.\nBleualign", "Gale-Church"])
	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)
	plt.legend(bbox_to_anchor=(0.0, 1.0), ncol=3, loc="lower left", borderaxespad=0.1)
	fig.set_size_inches(4,3)
	fig.tight_layout()
	fig.savefig(f"{out_dir}/precision_recall_f1.pdf")


def main():
	pr = read_precision_recall(in_dir)
	p1(pr)
	pr["f1"] = pr.apply(lambda x: get_f1(x["precision"], x["recall"]), axis=1)
	max_f1 = pr.groupby("aligner").agg(max_f1=pd.NamedAgg("f1", "max")).reset_index()
	max_f1 = max_f1.sort_values("max_f1", ascending=False)
	max_f1 = max_f1.drop(index=3) # Drop hunalign
	p2(max_f1)

	f1_pr = []
	for aligner, f1 in zip(max_f1["aligner"], max_f1["max_f1"]):
		temp = pr[(pr['aligner'] == aligner) & (pr["f1"] == f1)].drop("threshold", axis=1).drop_duplicates()
		f1_pr.append(temp)

	f1_pr = pd.concat(f1_pr)
	f1_pr = pd.melt(f1_pr, id_vars=["type", "aligner"])
	f1_pr["variable"] = f1_pr["variable"].apply(lambda x: x.title())
	p3(f1_pr)

if __name__ == "__main__":
	main()