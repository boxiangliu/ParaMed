# Train zh -> en on WMT18 data: 
# Do not run (only run on GPU nodes)
bash translation/wmt18/train.sh 

# Train zh -> en on WMT18 BPE data:
# Do not run (only run on GPU nodes)
bash translation/wmt18/train_bpe.sh

/mnt/home/boxiang/software/anaconda2/envs/py3/bin/python preprocess/translation.py \
--article_path_list ../processed_data/crawler/nejm/translation/input_list \
--out_dir ../processed_data/crawler/nejm/translation/