from typing import Any
import requests
import treelib


def get_options(data: dict[str, Any], show_label: bool = False) -> dict[str, Any]:
    options = {
        "title": {
            "text": "Dependency Tree",
            "subtext": "Dependency Tree",
            "show": False,
        },
        "tooltip": {
            "trigger": "item",
            "triggerOn": "mousemove",
            "show": show_label,
        },
        "series": [
            {
                "type": "tree",
                "data": [data],
                "left": "2%",
                "right": "2%",
                "top": "8%",
                "bottom": "20%",
                "symbol": "emptyCircle",
                "orient": "vertical",
                "expandAndCollapse": True,
                "initialTreeDepth": -1,
                "label": {
                    "position": "top",
                    "rotate": 0,
                    "verticalAlign": "middle",
                    "align": "center",
                    "fontSize": 16,
                },
                "leaves": {
                    "label": {
                        "position": "bottom",
                        "rotate": 0,
                        "verticalAlign": "middle",
                        "align": "center",
                        "fontSize": 16,
                    }
                },
                "animationDurationUpdate": 750,
            }
        ],
    }

    return options


def translate_bing(
    sentence: str,
    session_bing: requests.Session,
    language_from: str,
    language_to: str,
) -> str:
    base_url = "https://api.cognitive.microsofttranslator.com/translate"
    params = {"api-version": "3.0", "language": language_from, "to": language_to}

    body = [{"text": sentence}]

    request = session_bing.post(base_url, params=params, json=body)
    response = request.json()

    return response[0]["translations"][0]["text"]


def translate_google(
    sentence: str,
    session_google: requests.Session,
    language_from: str,
    language_to: str,
) -> str:
    google_api_key = "AIzaSyCbVPGnPE0imPF1r0eJYEdVWWj42HAYalo"
    url = "https://translation.googleapis.com/language/translate/v2"

    data = {
        "key": google_api_key,
        "source": language_from,
        "target": language_to,
        "q": sentence,
        "format": "text",
    }
    response = session_google.post(url, data)
    res = response.json()

    return res["data"]["translations"][0]["translatedText"]


def translate_deepl(
    sentence: str,
    session_deepl: requests.Session,
    language_to: str,
) -> str:
    url = "https://api.deepl.com/v2/translate"
    params = {
        "text": [sentence],
        "target_lang": language_to,
    }
    response = session_deepl.post(url, params=params)
    res = response.json()

    return res["translations"][0]["text"]


def make_list_from_tree(tree: treelib.Tree, node: treelib.Node):
    if node is None:
        return None
    if node.data is None:
        return None
    if len(list(node._successors.values())) == 0:
        return {
            "name": f"{node.data.type}\n{node.data.word}",
            "value": node.data.type,
        }

    return {
        "name": f"{node.data.type}\n{node.data.word}",
        "value": node.data.type,
        "children": [
            make_list_from_tree(tree, tree.nodes[child])
            for child in list(node._successors.values())[0]
        ],
    }
