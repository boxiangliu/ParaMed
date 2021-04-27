import pandas as pd
in_file = "../processed_data/clean/clean/all.rm_dup.txt"

corpus = pd.read_table(in_file, sep="\t", quoting=3, header=None, names=["article", "sentence", "zh", "en"])

# Number of articles
len(corpus["article"].unique())
# 1966

# Number of sentences:
corpus.shape[0]
# 97441

def get_tokens(sentences: list) -> list:
    '''
    INPUT ARGS
    sentences: [List] a list of sentences
    '''
    tokens = []
    for sentence in sentences:
        for token in sentence.split(" "):
            tokens.append(token)
    return tokens

en_tokens = get_tokens(corpus["en"].tolist())

# English
# Number of unique tokens
len(set(en_tokens))
# 55,673

# Number of tokens:
len(en_tokens)
# 3,028,434


# Chinese
zh_tokens = get_tokens(corpus["zh"].tolist())

# Number of unique tokens
len(set(zh_tokens))
# 46,700

# Number of tokens:
len(zh_tokens)
# 2,916,779


def get_avg_length(sentences: list) -> float:
    '''
    INPUT ARGS:
    sentences: [List] a list of sentences
    '''
    sentence_lengths = []
    for sentence in sentences:
        tokens = sentence.split(" ")
        sentence_lengths.append(len(tokens))

    return sum(sentence_lengths) / len(sentence_lengths)


def test_get_avg_length():
    sentences = ["a b c", "d e", "s d k l m"]
    avg_length = get_avg_length(sentences)
    assert avg_length == 10/3

# English sentence length
get_avg_length(corpus["en"].tolist())
# 31.080

# Chinese sentence length
get_avg_length(corpus["zh"].tolist())
# 29.934