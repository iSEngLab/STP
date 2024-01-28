import streamlit as st
from app.common import State

from app.romanian import common
from app.mt import commonApi

from streamlit_echarts import st_echarts


def render(state: State) -> None:
    st.title("Romanian-English")

    sentence = st.sidebar.text_area("Insert your sentence", key="input_text")
    clicked = st.sidebar.button("Translate", key="translate_button")

    if clicked:
        commonApi.read_conf()

        st.header("Sentence: ")
        st.write(sentence)

        # st.header("Constituency Tree: ")
        # main_sentence: commonApi.IndexTree = commonApi.IndexTree.fromstring(
        #     state.nlpEN.parse(sentence)
        # )
        # const_tree = main_sentence.makeList()

        # st_echarts(
        #     options=common.get_options(const_tree),
        #     key="echarts=const_tree",
        #     height="800px",
        # )

        st.header("Dependency Tree: ")
        doc = state.nlp(sentence)
        dep_tree = common.generate_dep_tree(doc)

        if dep_tree is not None:
            st_echarts(
                options=common.get_options(dep_tree, show_label=True),
                key="echarts=dep_tree",
                height="800px",
            )

        sentences = [sentence]

        st.header("Generated Sentences: ")
        for i, s in enumerate(sentences):
            st.header(f"#{i+1}")
            st.write(f"**Original sentence**: {s}")

            deepl_translation = common.translate_deepl(
                s,
                state.session_deepl,
                language_to="en",
            )
            st.write(f"***DeepL Translation***: {deepl_translation}")

            google_translation = common.translate_google(
                s,
                state.session_google,
                language_from="ro",
                language_to="en",
            )
            st.write(f"**Google Translation**: {google_translation}")

            bing_translation = common.translate_bing(
                s,
                state.session_bing,
                language_from="ro",
                language_to="en",
            )
            st.write(f"**Bing Translation**: {bing_translation}")