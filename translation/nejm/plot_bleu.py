import pandas as pd
import os
import matplotlib 
matplotlib.use('tkagg')
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import re
from collections import defaultdict

in_dir = "../processed_data/translation/nejm/finetune/test/"
out_dir = "../processed_data/translation/nejm/plot_bleu/"
os.makedirs(out_dir, exist_ok=True)


data = ["wmt18", "nejm.4000", "nejm.8000", "nejm.16000", \
	"nejm.32000", "nejm.64000", "nejm.93303"]
direction = ["zh2en", "en2zh"]
container = defaultdict(list)
for i in data:
	for j in direction:
		container["data"].append(i)
		container["direction"].append(j)
		fn = f"{in_dir}/{i}.{j}.tc.bleu"
		with open(fn, "r") as f:
			line = f.readlines()[0].strip()
			bleu = re.search("BLEU = [0-9\.]+", line).group(0).split("=")[1].strip()
			bleu = float(bleu)
			container["bleu"].append(bleu)

bleu = pd.DataFrame(container)

fig, ax = plt.subplots(1, 1)
sns.scatterplot(x="data", y="bleu", hue="direction", data=bleu, legend="full")
ax.set_xlabel("Sentence Pairs")
ax.set_ylabel("BLEU")
ax.set_xticklabels(["Baseline", "4000", "8000", "16000", "32000", "64000", "93303"])
ax.legend()
fig.set_size_inches(5,3)
fig.tight_layout()
plt.savefig(f"{out_dir}/bleu.pdf")
plt.close()
