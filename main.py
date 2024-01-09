import time
from typing import Any
import openpyxl
import common
import gen
import translate

# coreNLP放置位置

nlp_cn = common.nlpCN
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
setName = setList[9]
dataset = "./data/original_sentences/" + setName
thod = 0.7
# Bing Translate
bing_translate_api_key = ""
google_translate_api_key = ""
# bing target language: Chinese
bing_source_language = "en"
bing_target_language = "zh"
# Google target language: zh
google_source_language = "en"
google_target_language = "zh-cn"
# Youdao Target Language：
youdao_source_language = "en"
youdao_target_language = "zh"


def collect_target_sentences(
    translator: str,
    filtered_sent: dict[str, Any],
    source_language: str,
    target_language: str,
    api_key: str | None = None,
) -> dict[str, Any]:
    """
    收集翻译语句结果
    :param translator: 翻译器选择
    :param filtered_sent: 需要翻译的句子
    :param source_language: 原语句
    :param target_language: 目标语句
    :param api_key: 与翻译器交互的API Key
    :return: 需要翻译句子的字典
    """
    """Return Translation dic for a translator"""
    if translator == "Google":
        return translate.GoogleTranslate(
            api_key, filtered_sent, source_language, target_language
        )
    if translator == "Bing":
        return translate.BingTranslate(
            api_key, filtered_sent, source_language, target_language
        )
    if translator == "Youdao":
        return translate.YoudaoTranslate(
            filtered_sent, source_language, target_language
        )
    if translator == "DeepL":
        return translate.DeepLTranslate(filtered_sent, source_language, target_language)

    return {}


def gen_error(setname, datasetAfter, target_sentences, filename):
    """
    生成错误结果
    :param datasetAfter:
    :param target_sentences:
    :param nlpCN: Stanford CoreNlp 中文对象
    :param nlpEN:  Stanford CoreNlp 英文对象
    :param thod: 阈值
    :param filename:  读取扩增文件地址
    :return: 返回原语句：扩增语句的字典
    """

    wb = openpyxl.Workbook()
    ws = wb.create_sheet(setname)
    ws.append([])
    print("save Excel")

    ii = 0
    for sent in datasetAfter:
        tranSl = target_sentences[sent]
        ws.append(["issue: " + str(ii)])
        ws.append(["原句："])
        ws.append([sent])
        ws.append([tranSl])
        ii = ii + 1
        ws.append(["目的句："])

        for new in datasetAfter[sent]:
            tranCl = target_sentences[new]
            ws.append([new])
            ws.append([tranCl])
        ws.append([])
    save_path = filename
    wb.save(save_path)


time1 = time.time()
datasetAfter, notimport = gen.gen_all(setName)

target_sentences_google = collect_target_sentences(
    "Google", datasetAfter, google_source_language, google_target_language
)
target_sentences_bing = collect_target_sentences(
    "Bing",
    datasetAfter,
    bing_source_language,
    bing_target_language,
    bing_translate_api_key,
)
# target_sentences_youdao = collect_target_sentences("Youdao",datasetAfter,youdao_source_language,youdao_target_language)
gen_error(setName, datasetAfter, target_sentences_google, setName + "_google.xlsx")
gen_error(setName, datasetAfter, target_sentences_bing, setName + "_bing.xlsx")
# genError(setName,datasetAfter,target_sentences_youdao,setName+"_youdao.xlsx")
nlp_cn.close()
nlp_en.close()
time2 = time.time()
total_cost = time2 - time1
print(total_cost)
