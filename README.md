# ParaMed: A Parallel Corpus for Chinese-English Translation in the Medical Domain

## Description 
`NEJM` is a Chinese-English parallel corpus crawled from the New England Journal of Medicine website. English articles are distributed through <https://www.nejm.org/> and Chinese articles are distributed through <http://nejmqianyan.cn/>. The corpus contains all article pairs (around 2000 pairs) since 2011. 

This project was motivated by the fact that the Biomedical translation shared task in WMT19 did not provide training data for Chinese/English. In fact, we did not find any publically available parallel corpus between English and Chinese. We collected the `NEJM` corpus to faciliate machine translation between English and Chinese in the medical domain. We found that a remarkable boost in BLEU score can be achieved by pre-training on WMT18 and fine-tuning on the `NEJM` corpus. 


## Data Download 
You can download ~ 70% of data [here](https://github.com/boxiangliu/med_translation/blob/master/data/nejm-open-access.tar.gz?raw=true). Read on if you would like the entire dataset. 

The New England Journal of Medicine is a pay-for-access journal. We are therefore prohibited by their copyright policy to freely distribute the entire dataset. However, Journal Watch and Original Research articles are open access six months after the initial publication. These articles make up about ~ 70% of the entire dataset and you can access them immediately using the link above. 

If you are a NEJM subscriber through an institution or a personal account, as we belive most biomedical researchers are, you are entitled to access the full data. Please email us at <jollier.liu@gmail.com> for access to the entire dataset. 

## Installation & Prerequisite 

The code in this repository was written in `python 3.7`. 

First you need to clone the repository: 

	git clone https://github.com/boxiangliu/med_translation.git

Then install the following python packages if they are not installed yet. 

- selenium
- numpy
- pandas 
- matplotlib
- seaborn
- nltk

Also install these packages outside of python: 

- [eserix](https://github.com/emjotde/eserix)
- [bifixer](https://github.com/bitextor/bifixer)
- [Microsoft bilingual sentence aligner](https://www.microsoft.com/en-us/download/details.aspx?id=52608&from=https%3A%2F%2Fresearch.microsoft.com%2Fen-us%2Fdownloads%2Faafd5dcf-4dcc-49b2-8a22-f7055113e656%2F)
- [OpenNMT](https://github.com/OpenNMT/OpenNMT-py)

## Reproducing the paper

WARNING: Those without access to NEJM will likely not be able to run all steps in this repo. 

### 1. Crawl the NEJM website
In `crawl/crawl.py`, replace the value of `nejm_username` and `nejm_password` with your credentials. Then run: 

	python3 crawler/crawl.py

This step crawls thousands of articles from NEJM and will take a number of hours. 

### [Optional] Plot summary statistics of crawled articles

To plot the distribution of articles by year and by type, run: 

	python3 crawler/url_stat.py


### Filter crawled articles
The crawled articles are peppered with bits and pieces of noisy text. To remove them, run: 

	python3 crawler/filter.py

### [Optional] Compare pre- and post-filtered articles

To see the effect of filtering on article lengths, run:

	python3 crawler/article_stat.py

## 2. Preprocessing
We will normalize, break up paragraphs into sentences, tokenize and truecase. 

### Normalize punctuations

We will standardize English and Chinese punctuations. Run:  

	bash preprocess/normalize.sh

### Split paragraphs into sentences

We will split English and Chinese paragraphs into sentences using eserix: 

	bash preprocess/detect_sentences/eserix.sh 

### [Optional] Compare eserix with punkt

We can also split paragraphs with another popular python module called `punkt`, and compare the performance of the two algorithms. 

	python3 preprocess/detect_sentences/punkt.py
	python3 preprocess/detect_sentences/sent_stat.py

### Tokenize and truecase
The final preprocessing steps will be tokenization and truecasing

	bash preprocess/tokenize.sh
	bash preprocess/truecase.sh

## 3. Sentence alignment


### Manual alignment

In order to compare automatic sentence alignment algorithms, we need to establish a set of ground truth alignment. Lucky for you, we have done the dirty work of aligning sentences. You can download the raw sentences (unaligned) [here](https://github.com/boxiangliu/med_translation/blob/master/data/manual_align_input.tar.gz?raw=true). Create a directory and untar into this directory. These will be used as input to the sentence alignment algorithm below. 

	mkdir ../processed_data/preprocess/manual_align/input/
	cd ../processed_data/preprocess/manual_align/input/
	tar xzvf manual_align_input.tar.gz

Next download the manual alignment result [here](https://raw.githubusercontent.com/boxiangliu/med_translation/master/data/align.txt). Place it into the following directory. 

	mkdir ../processed_data/preprocess/manual_align/alignment/

The alignment result will be used to assess the quality of alignment algorithms. 


### Assessment of alignment algorithms

We assess the performance of [Gale-Church](https://www.aclweb.org/anthology/J93-1004.pdf) (length-based), [Microsoft aligner](https://www.microsoft.com/en-us/download/details.aspx?id=52608&from=https%3A%2F%2Fresearch.microsoft.com%2Fen-us%2Fdownloads%2Faafd5dcf-4dcc-49b2-8a22-f7055113e656%2F) (Lexicon-based), and [Bleualign](https://github.com/rsennrich/Bleualign) (translation-based). Install them on your system. 

Next run the following commands to align sentences using all algorithms.

#### Align with Moore's algorithm:
	bash evaluation/nejm/align/moore/input.sh
	bash evaluation/nejm/align/moore/align.sh

#### Align with Bleualign and Gale-Church algorithm:
	bash evaluation/nejm/align/bleualign/input.sh
	bash evaluation/nejm/align/bleualign/translate.sh
	bash evaluation/nejm/align/bleualign/align.sh

Evaluate the performance of all algorithms: 

	bash evaluation/nejm/evaluate.sh
	python3 evaluation/nejm/vis_pr_curve.py

### Align the entire corpus

In the manuscript, we found that the Microsoft aligner gave the best performance. We use it to align the entire corpus. 

	bash alignment/moore/input.sh
	bash alignment/moore/align.sh


## Clean the `NEJM` corpus
Some sentences such as paragraph headings will be duplicated many times. To remove them, run the following command: 

	bash clean/concat.sh
	bash clean/clean.sh

## Split the data into train, dev and test: 

Run the following to split data into train (~ 93000), development (~ 2000), and test (~ 2000): 

	bash split_data/split_train_test.py


## Translation

To determine whether `NEJM` helps improving machine translation in the biomedical domain, we first train a baseline model using WMT18 English/Chinese dataset and fine-tune the model on `NEJM`.

WMT18 preprocessed en/zh data can be downloaded [here](http://data.statmt.org/wmt18/translation-task/preprocessed/zh-en/). 

Train the baseline model:
	bash translation/wmt18/train.sh


Subset the dataset to see translation performance improvement at various corpus sizes. 

	python3 subset/subset.py

Fine-tune on NEJM dataset and test the fine-tune performance:

	python3 translation/nejm/finetune.sh
	python3 translation/nejm/test_finetune.sh


Train on `NEJM` from scratch (without using WMT18):

	python3 translation/nejm/train_denovo.sh
	python3 translation/nejm/test_denovo.sh


Plot bleu score:

	python3 translation/nejm/plot_bleu.py


## Questions? 

If you have any questions, please email us at <jollier.liu@gmail.com>
