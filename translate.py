import requests
import string
import time
import hashlib
import json
import uuid
import os

import six
from google.cloud import translate_v2 as translate

bing_api_key = ""
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./gcd.json"

google_api_key = "please enter your google api key"


def BingTranslate(api_key, filtered_sent, language_from, language_to):
    """Bing Microsoft translator
    If you encounter any issues with the base_url or path, make sure
    that you are using the latest endpoint:
    https://docs.microsoft.com/azure/cognitive-services/translator/reference/v3-0-translate
    Arguments:
    api_key = Bing Microsoft Translate API key
    filtered_sent = dictionary of original sentence to list of filtered sentences
    language_from = Source language code_ls
    language_to = Target language code_ls
    returns translation dictionary from source sentence to target sentence
    """
    dict_name = {}
    with open("temp2.txt", "r", encoding="utf-8") as fp:
        a = fp.read()
        dict_name = eval(a)
        fp.close()
    # headers = {'X-HTTP-Method-Override': 'GET'}
    # response = requests.post(url, data=data, headers=headers)

    base_url = "https://api.cognitive.microsofttranslator.com"
    path = "/translate?api-version=3.0"
    params = "&language=" + language_from + "&to=" + language_to
    constructed_url = base_url + path + params
    location = "global"
    headers = {
        "Ocp-Apim-Subscription-Key": bing_api_key,
        "Ocp-Apim-Subscription-Region": location,
        "Content-type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4()),
    }
    translation_dic = {}

    for sent in filtered_sent.keys():
        sent1 = sent.split("\n")[0]
        body = [{"text": sent1}]
        if dict_name.get(sent1, -1) != -1:
            result = dict_name[sent1]
            translation_dic[sent1] = result
            for new_s in filtered_sent[sent]:
                translation_dic[new_s] = dict_name[new_s]
        else:
            request = requests.post(
                constructed_url, params=params, headers=headers, json=body
            )
            response = request.json()
            result = (
                response[0]["translations"][0]["text"]
                .replace("&#39;", "'")
                .replace("&quot;", "'")
            )
            translation_dic[sent1] = result
            dict_name[sent1] = result

            body = [{"text": x} for x in filtered_sent[sent]]
            lenn = (int)(len(body) / 50)
            if len(body) == 0:
                continue
            for ii in range(lenn + 1):
                if ii == lenn:
                    body1 = body[ii * 50 : len(body)]
                else:
                    body1 = body[ii * 50 : (ii + 1) * 50]
                try:
                    request = requests.post(
                        constructed_url, params=params, headers=headers, json=body1
                    )
                except Exception:
                    time.sleep(100)
                    request = requests.post(
                        constructed_url, params=params, headers=headers, json=body1
                    )
                response = request.json()
                time.sleep(3)

                print(response)
                for i in range(len(body1)):
                    try:
                        dict_name[filtered_sent[sent][ii * 50 + i]] = (
                            response[i]["translations"][0]["text"]
                            .replace("&#39;", "'")
                            .replace("&quot;", "'")
                        )
                    except KeyError:
                        pass
                for i in range(len(body1)):
                    try:
                        translation_dic[filtered_sent[sent][ii * 50 + i]] = (
                            response[i]["translations"][0]["text"]
                            .replace("&#39;", "'")
                            .replace("&quot;", "'")
                        )
                    except KeyError:
                        pass
            f = open("temp2.txt", "w", encoding="utf-8")
            f.write(str(dict_name))
            f.close()
    return translation_dic


def GoogleTranslate(api_key, filtered_sent, source_language, target_language):
    """Google Translate, visit https://cloud.google.com/translate/docs to know pre-requisites
    Arguments:
    filtered_sent = dictionary of original sentence to list of filtered sentences
    source_language = Source language code_ls
    target_language = Target language code_ls
    returns translation dictionary from source sentence to target sentence
    """
    url = "https://translation.googleapis.com/language/translate/v2"
    # 读取
    dict_name = {}
    with open("temp.txt", "r", encoding="utf-8") as fp:
        a = fp.read()
        dict_name = eval(a)
        fp.close()
    # headers = {'X-HTTP-Method-Override': 'GET'}
    # response = requests.post(url, data=data, headers=headers)

    # print(response.json())
    translation_dic = {}
    for sent in filtered_sent.keys():
        sent1 = sent.split("\n")[0]
        data = {
            "key": google_api_key,
            "source": source_language,
            "target": target_language,
            "q": sent1,
            "format": "text",
        }
        if dict_name.get(sent1, -1) != -1:
            result = dict_name[sent1]
        else:
            try:
                response = requests.post(url, data)
            except Exception:
                time.sleep(100)
                response = requests.post(url, data)
            res = response.json()
            result = res["data"]["translations"][0]["translatedText"]
            print(res["data"]["translations"][0]["translatedText"])
            dict_name[sent1] = result
        translation_dic[sent1] = result
        for new_s in filtered_sent[sent]:
            data["q"] = new_s
            if dict_name.get(new_s, -1) != -1:
                result = dict_name[new_s]
            else:
                try:
                    response = requests.post(url, data)
                except Exception:
                    time.sleep(100)
                    response = requests.post(url, data)
                res = response.json()
                result = res["data"]["translations"][0]["translatedText"]
                dict_name[new_s] = result
            translation_dic[new_s] = result
        f = open("temp.txt", "w", encoding="utf-8")
        f.write(str(dict_name))
        f.close()

    return translation_dic


# youdaoAPI
YOUDAO_URL = "https://openapi.youdao.com/api"
APP_KEY = ""
APP_SECRET = ""


def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode("utf-8"))
    return hash_algorithm.hexdigest()


def truncate(q) -> str:
    if q is None:
        return ""
    size = len(q)
    return q if size <= 20 else q[0:10] + str(size) + q[size - 10 : size]


def do_request(data):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    return requests.post(YOUDAO_URL, data=data, headers=headers)


def youdao_translate(source_sentence, source_language, target_language):
    """
    有道翻译
    :param source_sentence: 源语句
    :param source_language: 源语言
    :param target_language: 目的语言
    :return:
    """
    target_sentence = ""

    q = source_sentence

    data = {}
    data["from"] = source_language
    data["to"] = target_language
    data["signType"] = "v3"
    curtime = str(int(time.time()))
    data["curtime"] = curtime
    salt = str(uuid.uuid1())
    signStr = APP_KEY + truncate(q) + salt + curtime + APP_SECRET
    sign = encrypt(signStr)
    data["appKey"] = APP_KEY
    data["q"] = q
    data["salt"] = salt
    data["sign"] = sign
    data["vocabId"] = "您的用户词表ID"

    response = do_request(data)
    contentType = response.headers["Content-Type"]
    if contentType == "audio/mp3":
        millis = int(round(time.time() * 1000))
        filePath = "合成的音频存储路径" + str(millis) + ".mp3"
        fo = open(filePath, "wb")
        fo.write(response.content)
        fo.close()
    else:
        target_sentence = response.json()["translation"][0]
    return target_sentence


def deepl_translate(source_sentence, source_language, target_language):
    """
    有道翻译
    :param source_sentence: 源语句
    :param source_language: 源语言
    :param target_language: 目的语言
    :return:
    """
    target_sentence = ""

    q = source_sentence

    data = {}
    data["from"] = source_language
    data["to"] = target_language
    data["signType"] = "v3"
    curtime = str(int(time.time()))
    data["curtime"] = curtime
    salt = str(uuid.uuid1())
    signStr = APP_KEY + truncate(q) + salt + curtime + APP_SECRET
    sign = encrypt(signStr)
    data["appKey"] = APP_KEY
    data["q"] = q
    data["salt"] = salt
    data["sign"] = sign
    data["vocabId"] = "您的用户词表ID"

    response = do_request(data)
    contentType = response.headers["Content-Type"]
    if contentType == "audio/mp3":
        millis = int(round(time.time() * 1000))
        filePath = "合成的音频存储路径" + str(millis) + ".mp3"
        fo = open(filePath, "wb")
        fo.write(response.content)
        fo.close()
    else:
        target_sentence = response.json()["translation"][0]
    return target_sentence


def YoudaoTranslate(filtered_sent, source_language, target_language):
    translation_dic = {}
    for sent in filtered_sent.keys():
        sent1 = sent.split("\n")[0]
        result = youdao_translate(
            source_sentence=sent1,
            source_language=source_language,
            target_language=target_language,
        )
        translation_dic[sent1] = result
        for new_s in filtered_sent[sent]:
            result = youdao_translate(
                source_sentence=new_s,
                source_language=source_language,
                target_language=target_language,
            )
            translation_dic[new_s] = result

    return translation_dic


def DeepLTranslate(filtered_sent, source_language, target_language):
    translation_dic = {}
    for sent in filtered_sent.keys():
        sent1 = sent.split("\n")[0]
        result = youdao_translate(
            source_sentence=sent1,
            source_language=source_language,
            target_language=target_language,
        )
        translation_dic[sent1] = result
        for new_s in filtered_sent[sent]:
            result = youdao_translate(
                source_sentence=new_s,
                source_language=source_language,
                target_language=target_language,
            )
            translation_dic[new_s] = result

    return translation_dic


def bing_translate(source_sentence, source_language, target_language):
    """
    bing翻译接口
    :param source_sentence: 源语句
    :param source_language: 源语言
    :param target_language: 目的语言
    :return:
    """
    base_url = "https://api.cognitive.microsofttranslator.com"
    path = "/translate?api-version=3.0"
    params = "&language=" + source_language + "&to=" + target_language
    constructed_url = base_url + path + params
    location = "global"
    headers = {
        "Ocp-Apim-Subscription-Key": bing_api_key,
        "Ocp-Apim-Subscription-Region": location,
        "Content-type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4()),
    }
    sent1 = source_sentence.split("\n")[0]
    body = [{"text": sent1}]
    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    response = request.json()
    result = (
        response[0]["translations"][0]["text"]
        .replace("&#39;", "'")
        .replace("&quot;", "'")
    )
    target_sentence = result
    return target_sentence


# 请求不能高于每秒1次
def baidu_translate(
    source_sentence: str,
    source_language: str,
    target_language: str,
) -> str:
    """
    百度翻译接口
    :param source_sentence: 源语句
    :param source_language: 源语言
    :param target_language: 目标语言
    :return:
    """
    target_sentence = ""
    api_url = "http://api.fanyi.baidu.com/api/trans/vip/translate"
    my_appid = "20210428000806448"
    cyber = "k0khaHHFd4CXQFJgWf7G"
    lower_case = list(string.ascii_lowercase)
    salt = str(time.time())[:10]
    final_sign = str(my_appid) + source_sentence + salt + cyber
    final_sign = hashlib.md5(final_sign.encode("utf-8")).hexdigest()
    # 区别en,zh构造请求参数
    if list(source_sentence)[0] in lower_case:
        paramas = {
            "q": source_sentence,
            "from": source_language,
            "to": target_language,
            "appid": "%s" % my_appid,
            "salt": "%s" % salt,
            "sign": "%s" % final_sign,
        }
        # my_url = (
        #     api_url
        #     + "?appid="
        #     + str(my_appid)
        #     + "&q="
        #     + source_sentence
        #     + "&from="
        #     + "en"
        #     + "&to="
        #     + "zh"
        #     + "&salt="
        #     + salt
        #     + "&sign="
        #     + final_sign
        # )
    else:
        paramas = {
            "q": source_sentence,
            "from": source_language,
            "to": target_language,
            "appid": "%s" % my_appid,
            "salt": "%s" % salt,
            "sign": "%s" % final_sign,
        }
    response = requests.get(api_url, params=paramas).content
    content = str(response, encoding="utf-8")
    json_reads = json.loads(content)
    target_sentence = json_reads["trans_result"][0]["dst"]
    return target_sentence


def google_translate(text, source, target) -> str:
    """Translates text into the target language.
    Target must be an ISO 639-1 language code_ls.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """

    translate_client = translate.Client()

    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in
    # which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target)

    print("Text: {}".format(result["input"]))
    print("Translation: {}".format(result["translatedText"]))
    print("Detected source language: {}".format(result["detectedSourceLanguage"]))
    return result["translatedText"]


if __name__ == "__main__":
    dict_name = {1: {1: 2, 3: 4}, 2: {3: 4, 4: 5}}
    f = open("temp.txt", "w")
    f.write(str(dict_name))
    f.close()

    # 读取
    f = open("temp.txt", "r")
    a = f.read()
    dict_name = eval(a)
    f.close()
    # print(google_translate("hello",'en','zh'))
