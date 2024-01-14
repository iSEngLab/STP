import requests
import time
import uuid
import os


os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"
] = "/home/ioachimlihor/.config/gcloud/application_default_credentials.json"


def BingTranslate(filtered_sent, language_from, language_to):
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
    bing_api_key = "8a3ac4d9c987447790443ec9024496b2"

    dict_name = {}
    with open("temp_bing.txt", "r", encoding="utf-8") as fp:
        a = fp.read()
        dict_name = eval(a)
        fp.close()
    # headers = {'X-HTTP-Method-Override': 'GET'}
    # response = requests.post(url, data=data, headers=headers)

    base_url = "https://api.cognitive.microsofttranslator.com/translate"
    location = "global"
    headers = {
        "Ocp-Apim-Subscription-Key": bing_api_key,
        "Ocp-Apim-Subscription-Region": location,
        "Content-type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4()),
    }
    params = {"api-version": "3.0", "language": language_from, "to": language_to}

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
            request = requests.post(base_url, params=params, headers=headers, json=body)
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
                        base_url, params=params, headers=headers, json=body1
                    )
                except Exception:
                    time.sleep(100)
                    request = requests.post(
                        base_url, params=params, headers=headers, json=body1
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
            f = open("temp_bing.txt", "w", encoding="utf-8")
            f.write(str(dict_name))
            f.close()
    return translation_dic


def GoogleTranslate(filtered_sent, source_language, target_language):
    """Returns Google Translate translator. Visit https://cloud.google.com/translate/docs to know pre-requisites.

    Args:
        filtered_sent: dictionary of original sentence to list of filtered sentences
        source_language: Source language code_ls
        target_language: Target language code_ls
    Returns:
        translation dictionary from source sentence to target sentence
    """
    google_api_key = "AIzaSyBeebtYCCTfS71EKL4MzhzaM_DkCZpl1Uk"

    url = "https://translation.googleapis.com/language/translate/v2"
    # 读取
    dict_name = {}
    with open("temp_google.txt", "r", encoding="utf-8") as fp:
        a = fp.read()
        dict_name = eval(a)

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
        f = open("temp_google.txt", "w", encoding="utf-8")
        f.write(str(dict_name))
        f.close()

    return translation_dic


def DeepLTranslate(filtered_sent, target_language):
    """Returns DeepL Translate translator.

    Args:
        filtered_sent: dictionary of original sentence to list of filtered sentences
        target_language: Target language code_ls
    Returns:
        translation dictionary from source sentence to target sentence
    """
    url = "https://api.deepl.com/v2/translate"
    # 读取
    dict_name = {}
    with open("temp_deepl.txt", "r", encoding="utf-8") as fp:
        a = fp.read()
        dict_name = eval(a)

    # headers = {'X-HTTP-Method-Override': 'GET'}
    # response = requests.post(url, data=data, headers=headers)

    yourAuthKey = "bd17fa0a-8bda-95e9-2821-9549d6733ba8"
    headers = {"Authorization": f"DeepL-Auth-Key {yourAuthKey}"}

    # print(response.json())
    translation_dic = {}
    for sent in filtered_sent.keys():
        sent1 = sent.split("\n")[0]
        data = {
            "text": [sent1],
            "target_lang": target_language,
        }
        if dict_name.get(sent1, -1) != -1:
            result = dict_name[sent1]
        else:
            try:
                response = requests.post(url, data, headers=headers)
            except Exception:
                time.sleep(100)
                response = requests.post(url, data, headers=headers)
            res = response.json()
            result = res["translations"][0]["text"]
            print(result)
            dict_name[sent1] = result
        translation_dic[sent1] = result
        for new_s in filtered_sent[sent]:
            data["text"] = [new_s]
            if dict_name.get(new_s, -1) != -1:
                result = dict_name[new_s]
            else:
                try:
                    response = requests.post(url, data, headers=headers)
                except Exception:
                    time.sleep(100)
                    response = requests.post(url, data, headers=headers)
                res = response.json()
                result = res["translations"][0]["text"]
                dict_name[new_s] = result
            translation_dic[new_s] = result
        f = open("temp_deepl.txt", "w", encoding="utf-8")
        f.write(str(dict_name))
        f.close()

    return translation_dic
