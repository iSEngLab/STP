import string

from nltk import TreebankWordDetokenizer
from stanfordcorenlp import StanfordCoreNLP

stanford_nlp_path = "./stanford-corenlp-4.5.5"
nlpEN = StanfordCoreNLP(stanford_nlp_path)
nlpCN = StanfordCoreNLP(stanford_nlp_path, lang="zh")
de_tokenizer = TreebankWordDetokenizer()
punctuation_en = string.punctuation

"""global variable"""
clauses_tokens = []
inseparable = []
trunk = []
relationship = {}
tokens = []
remove_tree_dist = {}
pair = {}
parent = ""
sentences_gen = []
retain_tokens = []
