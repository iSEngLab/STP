from app.common import State
import spacy_streamlit


def render(state: State) -> None:
    spacy_streamlit.visualize(
        models=["en_core_web_sm", "ro_core_news_lg"],
        default_text="Those kinds of stakes we look to monetize smartly over time.",
        visualizers=["parser", "ner"],
        color="purple",
    )
