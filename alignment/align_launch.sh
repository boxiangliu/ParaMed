for i in {000..102}; do
sbatch --job-name=align${i} --ntasks 1 --cpus-per-task 4 --gres=gpu:1 --wrap "/mnt/home/boxiang/software/anaconda2/envs/py3/bin/python preprocess/align_semantic.py \
					--article_path ../processed_data/crawler/nejm/articles_norm/ \
					--article_path_list ../processed_data/crawler/nejm/pairs/article_paths/chunk${i} \
					--out_dir ../processed_data/crawler/nejm/pairs/sentence_pairs/" --partition=TitanXx8 --output=../processed_data/crawler/nejm/pairs/sentence_pairs/chunk${i}.slurm
done

