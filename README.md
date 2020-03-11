# NEJM: A Parallel Corpus for Chinese-English Translation in the Medical Domain

## Description 
`NEJM` is a Chinese-English parallel corpus crawled from the New England Journal of Medicine website. English articles are distributed through <https://www.nejm.org/> and Chinese articles are distributed through <http://nejmqianyan.cn/>. The corpus contains all article pairs (around 2000 pairs) since 2011. 

This project was motivated by the fact that the Biomedical translation shared task in WMT19 did not provide training data for Chinese/English. In fact, we did not find any publically available parallel corpus between English and Chinese. We collected the `NEJM` corpus to faciliate machine translation between English and Chinese in the medical domain. We found that a remarkable boost in BLEU score can be achieved by pre-training on WMT18 and fine-tuning on the `NEJM` corpus. 


## Data Download 
You can download ~ 70% of data using [here](https://github.com/boxiangliu/med_translation/blob/master/data/nejm-open-access.tar.gz?raw=true). Read on if you would like the entire dataset. 

The New England Journal of Medicine is a pay-for-access journal. We are therefore prohibited by their copyright policy to freely distribute the entire dataset. However, Journal Watch and Original Research articles are open access six months after the initial publication. These articles make up about ~ 70% of the entire dataset and you can access them immediately using the link above. 

If you are a NEJM subscriber through an institution or a personal account, as we belive most biomedical researchers are, you are entitled to access the full data. Please email us at <jollier.liu@gmail.com> for access to the entire dataset. 

## Installation & Prerequisite 


## Reproducing the paper