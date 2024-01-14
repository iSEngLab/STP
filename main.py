import os
import time
from typing import Any
import openpyxl
import common
import gen
import translate
import pickle

# coreNLP放置位置

nlp_en = common.nlpEN
# 数据集名称
setList = [
    "Politics",
    "Business",
    "Culture",
    "Sports",
    "Tech",
    "TravelFood",
    "Health",
    "LifeStyle",
    "Legal",
    "Opinion",
    "Business_Old",
    "Politics_Old",
]
setName = "Tech"
dataset = "./data/" + setName
thod = 0.7
# Bing Translate
bing_translate_api_key = ""
google_translate_api_key = ""
# bing target language: Chinese
source_language = "en"
target_language = "ro"


def collect_target_sentences(
    translator: str,
    filtered_sent: dict[str, Any],
    source_lang: str,
    target_lang: str,
) -> dict[str, Any]:
    """Returns Translation dictionary for a translator.

    Args:
        translator:
        filtered_sent:
        source_language:
        target_language:
    """
    if translator == "Google":
        return translate.GoogleTranslate(filtered_sent, source_lang, target_lang)
    if translator == "Bing":
        return translate.BingTranslate(filtered_sent, source_lang, target_lang)
    if translator == "DeepL":
        return translate.DeepLTranslate(filtered_sent, target_lang)

    return {}


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


time1 = time.time()
if not os.path.exists(f"datasetAfter_{setName}.pkl"):
    datasetAfter, notimport = gen.gen_all(setName)

    with open(f"datasetAfter_{setName}.pkl", "wb") as f:
        pickle.dump(datasetAfter, f)
    with open(f"notimport_{setName}.pkl", "wb") as f:
        pickle.dump(notimport, f)

with open(f"datasetAfter_{setName}.pkl", "rb") as f:
    datasetAfter = pickle.load(f)
with open(f"notimport_{setName}.pkl", "rb") as f:
    notimport = pickle.load(f)

if not os.path.exists(f"target_sentences_google_{setName}.pkl"):
    target_sentences_google = collect_target_sentences(
        "Google",
        datasetAfter,
        source_language,
        target_language,
    )
    with open(f"target_sentences_google_{setName}.pkl", "wb") as f:
        pickle.dump(target_sentences_google, f)

if not os.path.exists(f"target_sentences_bing_{setName}.pkl"):
    target_sentences_bing = collect_target_sentences(
        "Bing",
        datasetAfter,
        source_language,
        target_language,
    )
    with open(f"target_sentences_bing_{setName}.pkl", "wb") as f:
        pickle.dump(target_sentences_bing, f)

if not os.path.exists(f"target_sentences_deepl_{setName}.pkl"):
    target_sentences_deepl = collect_target_sentences(
        "DeepL",
        datasetAfter,
        source_language,
        target_language,
    )
    with open(f"target_sentences_deepl_{setName}.pkl", "wb") as f:
        pickle.dump(target_sentences_deepl, f)


with open(f"target_sentences_google_{setName}.pkl", "rb") as f:
    target_sentences_google = pickle.load(f)

with open(f"target_sentences_bing_{setName}.pkl", "rb") as f:
    target_sentences_bing = pickle.load(f)

with open(f"target_sentences_deepl_{setName}.pkl", "rb") as f:
    target_sentences_deepl = pickle.load(f)

# target_sentences_youdao = collect_target_sentences("Youdao",datasetAfter,youdao_source_language,youdao_target_language)
gen_error(setName, datasetAfter, target_sentences_google, setName + "_google.xlsx")
gen_error(setName, datasetAfter, target_sentences_bing, setName + "_bing.xlsx")
gen_error(setName, datasetAfter, target_sentences_deepl, setName + "_deepl.xlsx")
# genError(setName,datasetAfter,target_sentences_youdao,setName+"_youdao.xlsx")
nlp_en.close()
time2 = time.time()
total_cost = time2 - time1
print(total_cost)
