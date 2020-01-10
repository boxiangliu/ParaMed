import glob
import pandas as pd

out_dir = "../processed_data/crawler/nejm/urls/"

df = pd.DataFrame()
for fn in glob.glob(f"{out_dir}/*/*.txt"):
	print(f"Filename: {fn}")
	df.append(pd.read_table(fn, header=None))
