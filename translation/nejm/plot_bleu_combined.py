import pandas as pd
import os
import matplotlib 
matplotlib.use('tkagg')
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import re
from collections import defaultdict

denovo_xfmr_dir = "../processed_data/translation/nejm/train_denovo/test/"
finetune_xfmr_dir = "../processed_data/translation/nejm/finetune/test/"
denovo_lstm_dir = "../processed_data/translation/nejm/train_denovo_rnn/test/"
finetune_lstm_dir = "../processed_data/translation/nejm/finetune_rnn/test/"

out_dir = "../processed_data/translation/nejm/plot_bleu/"
os.makedirs(out_dir, exist_ok=True)


def get_plotting_data(denovo_dir, finetune_dir):
    data = ["wmt18", "nejm.4000", "nejm.8000", "nejm.16000", \
        "nejm.32000", "nejm.64000", "nejm.93303"]
    direction = ["zh2en", "en2zh"]
    container = defaultdict(list)
    for h, in_dir in [("de novo", denovo_dir), ("finetune", finetune_dir)]:
        for i,d in enumerate(data):
            for j in direction:
                fn = f"{in_dir}/{d}.{j}.tc.bleu"
                try:
                    with open(fn, "r") as f:
                        line = f.readlines()[0].strip()
                        bleu = re.search("BLEU = [0-9\.]+", line).group(0).split("=")[1].strip()
                        bleu = float(bleu)
                        container["bleu"].append(bleu)

                    container["data_ord"].append(i)
                    container["data"].append(d)
                    container["direction"].append(j)
                    container["train"].append(h)
                except:
                    print(f"{fn} does not exist.")

    bleu = pd.DataFrame(container)
    zeros = pd.DataFrame({"bleu":[0, 0], "data_ord": [0, 0], "data": ["nejm.0", "nejm.0"], "direction":["zh2en", "en2zh"], "train": ["de novo", "de novo"]})
    bleu = pd.concat([zeros, bleu])
    ord2num = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 5.46}
    bleu["x"] = bleu["data_ord"].apply(lambda x: ord2num[x])

    return bleu

bleu_xfmr = get_plotting_data(denovo_xfmr_dir, finetune_xfmr_dir)
bleu_lstm = get_plotting_data(denovo_lstm_dir, finetune_lstm_dir)
bleu_xfmr["model"] = "Transformer"
bleu_lstm["model"] = "LSTM"
bleu = pd.concat([bleu_lstm, bleu_xfmr])

plt.ion()
g = sns.FacetGrid(bleu, col="model", height=4, aspect=1, legend_out=False)
g.map_dataframe(sns.lineplot, x="x", y="bleu", hue="direction", legend="brief", style="train", markers=["o","o"], dashes=[(2,1),""])
g.add_legend()
g.set_titles(col_template="{col_name}")
g.set_axis_labels("In-Domain Sentence Pairs", "1-ref BLEU")
g.set(xticks=[0, 1, 2, 3, 4, 5, 5.46])
g.set(xticklabels=["0", "4000", "8000", "16000", "32000", "64000", ""])
g.tight_layout()
g.savefig(f"{out_dir}/bleu.pdf")
plt.close()