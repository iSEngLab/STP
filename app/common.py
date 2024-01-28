import uuid
import requests
import spacy
import streamlit as st

import app.mt.commonApi as commonApi

from stanfordcorenlp import StanfordCoreNLP


class State:
    def __init__(self) -> None:
        commonApi.read_conf()
        stanford_nlp_path = "./stanford-corenlp-4.5.5"
        self.nlpEN = StanfordCoreNLP(stanford_nlp_path)

        # Session for Microsoft Bing Translator
        self.session_bing = requests.Session()
        self.session_bing.headers = {
            "Ocp-Apim-Subscription-Key": "8a3ac4d9c987447790443ec9024496b2",
            "Ocp-Apim-Subscription-Region": "global",
            "Content-type": "application/json",
            "X-ClientTraceId": str(uuid.uuid4()),
        }

        # Session for Google Translator
        self.session_google = requests.Session()

        # Session for DeepL Translator
        self.session_deepl = requests.Session()
        self.session_deepl.headers = {
            "Authorization": "DeepL-Auth-Key bd17fa0a-8bda-95e9-2821-9549d6733ba8"
        }

        self.nlp = spacy.load("ro_core_news_lg")


def get_state() -> State:
    if "state" not in st.session_state:
        print("WARNING: new state created")
        st.session_state["state"] = State()

    return st.session_state["state"]
