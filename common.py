import string

from nltk import TreebankWordDetokenizer
from stanfordcorenlp import StanfordCoreNLP

stanford_nlp_path = r'/root/stanford-corenlp-4.1.0'
nlpEN = StanfordCoreNLP(stanford_nlp_path)
nlpCN = StanfordCoreNLP(stanford_nlp_path,lang='zh')
de_tokenizer = TreebankWordDetokenizer()
punctuation_en = string.punctuation  # 字符串的标点符号

"""global variable"""
clauses_tokens = []  # 识别到的从句的tokens
inseparable = []  # 识别到的不可拆词
trunk = []  # 主干部分token位置
relationship = {}
tokens = []  # 每个句子的全部token
remove_tree_dist = {}
pair = {}
parent = ""
sentences_gen = []
retain_tokens = []  # 需要保留的token 不能正常删除
