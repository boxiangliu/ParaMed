# NEJM: A Parallel Corpus for Chinese-English Translation in the Medical Domain

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






