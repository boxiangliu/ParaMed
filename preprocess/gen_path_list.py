import glob

article_dir = "../processed_data/crawler/nejm/articles_norm/"
article_paths = glob.glob("{}/*.en".format(article_dir))
out_dir = "../processed_data/crawler/nejm/pairs/article_paths/"

batch_size = 20
for i in range(0, len(article_paths), batch_size):
	batch = article_paths[i:i+batch_size]
	out_fn = "{}/chunk{:03d}".format(out_dir, int(i/batch_size))
	with open(out_fn, "w+") as f:
		for line in batch:
			en_path = line
			zh_path = line.replace(".en", ".zh")
			output = "{}\t{}\n".format(en_path, zh_path)
			f.write(output)

