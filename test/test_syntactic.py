import os

import common
from commonApi import read_conf
from gen import gen
from syntactic import find_clauses
import openpyxl

original_sentences = []


def read_original_sentences():
    global original_sentences
    original_sentences_root_path = r"..\data\original_sentences"
    for p in os.listdir(original_sentences_root_path):
        current_path = r"%s\%s" % (original_sentences_root_path, p)
        with open(current_path, encoding="utf8") as f:
            original_sentences += [x.strip() for x in f.readlines()]
            f.close()


def read_original_sentences_topic(topic):
    sentences = []
    original_sentences_path = r"..\data\original_sentences\%s" % topic
    with open(original_sentences_path, encoding="utf8") as f:
        sentences += [y.strip() for y in f.readlines()]
        f.close()
    return sentences


def write_source_gen(topic):
    path = "../output/%s.xlsx" % topic
    workbook = openpyxl.Workbook()
    sheet = workbook.create_sheet(title="生成句")

    sources = read_original_sentences_topic(topic)
    for source_sentence in sources:
        print(source_sentence)
        gen_sentences = gen(source_sentence)
        sheet.append(["原句:", ])
        sheet.append([source_sentence, ])
        sheet.append(["生成句:", ])
        for gen_sentence in gen_sentences:
            sheet.append([gen_sentence, ])
        sheet.append(['', ])
    workbook.save(path)


def test_single_sentence(s: str):
    print(s)
    print(find_clauses(s))


if __name__ == '__main__':
    read_conf("../related-documentation/Relationship")
    write_source_gen("Politics")
    common.nlpEN.close()
