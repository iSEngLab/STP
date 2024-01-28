import os
import pickle

import openpyxl

import common
from commonApi import read_conf
import gen
from transformers import pipeline

# model_checkpoint = "Helsinki-NLP/opus-mt-en-ro"
# model_checkpoint = "Helsinki-NLP/opus-tatoeba-en-ro"
# model_checkpoint = "Helsinki-NLP/opus-mt-tc-big-en-ro"
# model_checkpoint = "facebook/mbart-large-en-ro"
# model_checkpoint = "BlackKakapo/opus-mt-en-ro"

for dataset, model_checkpoint in [
    ("Opinion", "Helsinki-NLP/opus-mt-en-ro"),
    ("Opinion", "Helsinki-NLP/opus-tatoeba-en-ro"),
    ("Opinion", "Helsinki-NLP/opus-mt-tc-big-en-ro"),
    ("Opinion", "facebook/mbart-large-en-ro"),
    ("Opinion", "BlackKakapo/opus-mt-en-ro"),
    ("Tech", "Helsinki-NLP/opus-mt-en-ro"),
    ("Tech", "Helsinki-NLP/opus-tatoeba-en-ro"),
    ("Tech", "Helsinki-NLP/opus-mt-tc-big-en-ro"),
    ("Tech", "facebook/mbart-large-en-ro"),
    ("Tech", "BlackKakapo/opus-mt-en-ro"),
]:
    model_checkpoint_name = model_checkpoint.replace("/", "_").replace("-", "_")
    translator = pipeline(task="translation", model=model_checkpoint)
    read_conf()

    # dataset = sys.argv[1]
    orig_sent = []
    gen_sent = []
    gen_sen_translate = []

    def gen_error(setname, datasetAfter, target_sentences, filename):
        wb = openpyxl.Workbook()
        ws = wb.create_sheet(setname)
        ws.append([])
        print("save Excel")

        ii = 0
        for sent in datasetAfter:
            try:
                tranSl = target_sentences[sent]
            except Exception:
                break
            ws.append(["issue: " + str(ii)])
            ws.append(["Original sentence:"])
            ws.append([sent])
            ws.append([tranSl])
            ii = ii + 1
            ws.append(["Purpose sentence:"])

            for new in datasetAfter[sent]:
                try:
                    tranCl = target_sentences[new]
                except Exception:
                    break
                ws.append([new])
                ws.append([tranCl])
            ws.append([])
        save_path = filename
        wb.save(save_path)

    def custom_translate(filtered_sent, translator):
        translation_dic = {}
        for sent in filtered_sent.keys():
            sent1 = sent.split("\n")[0]
            if model_checkpoint == "facebook/mbart-large-en-ro":
                result = translator(sent, src_lang="en_XX", tgt_lang="ro_RO")[0][
                    "translation_text"
                ]
            else:
                result = translator(sent)[0]["translation_text"]
            print(result)
            translation_dic[sent1] = result
            for new_s in filtered_sent[sent]:
                if model_checkpoint == "facebook/mbart-large-en-ro":
                    result = translator(new_s, src_lang="en_XX", tgt_lang="ro_RO")[0][
                        "translation_text"
                    ]
                else:
                    result = translator(new_s)[0]["translation_text"]
                translation_dic[new_s] = result
        return translation_dic

    if not os.path.exists(f"datasetAfter_{dataset}_.pkl"):
        datasetAfter, notimport = gen.gen_all(dataset)

        with open(f"datasetAfter_{dataset}.pkl", "wb") as f:
            pickle.dump(datasetAfter, f)
        with open(f"notimport_{dataset}.pkl", "wb") as f:
            pickle.dump(notimport, f)

    with open(f"datasetAfter_{dataset}.pkl", "rb") as f:
        datasetAfter = pickle.load(f)
    with open(f"notimport_{dataset}.pkl", "rb") as f:
        notimport = pickle.load(f)

    if not os.path.exists(
        f"target_sentences_custom_{dataset}_{model_checkpoint_name}.pkl"
    ):
        target_sentences_custom = custom_translate(datasetAfter, translator)

        with open(
            f"target_sentences_custom_{dataset}_{model_checkpoint_name}.pkl", "wb"
        ) as f:
            pickle.dump(target_sentences_custom, f)

    with open(
        f"target_sentences_custom_{dataset}_{model_checkpoint_name}.pkl", "rb"
    ) as f:
        target_sentences_custom = pickle.load(f)

    gen_error(
        dataset,
        datasetAfter,
        target_sentences_custom,
        dataset + model_checkpoint_name + "_custom.xlsx",
    )

common.nlpEN.close()
