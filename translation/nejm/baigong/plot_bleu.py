import pandas as pd
import os
import matplotlib.pyplot as plt

out_dir = "../processed_data/translation/nejm/baigong/plot_bleu/"
os.makedirs(out_dir, exist_ok=True)

df = pd.DataFrame({"Pairs":[0, 4000, 8000, 16000, 32000, 64000, 90861],
	"BLEU":[23.16, 36.68, 41.74, 44.10, 45.13, 47.03, 47.70]})
plt.scatter(x="Pairs", y="BLEU", data=df)
plt.xlabel("Sentence Pairs")
plt.ylabel("BLEU")
plt.savefig(f"{out_dir}/bleu.pdf")