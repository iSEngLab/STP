import logging

import streamlit as st

from app.common import get_state
from app.about import renderer as about_renderer
from app.home import renderer as home_renderer
from app.romanian import renderer as romanian_renderer
from app.analyzer import renderer as analyzer_renderer


def init_logging() -> None:
    logging.basicConfig(level=logging.DEBUG)


def main() -> None:
    init_logging()
    state = get_state()

    PAGES = {
        "Home": home_renderer.render,
        "Ro-En": romanian_renderer.render,
        "Analyzer": analyzer_renderer.render,
        "About us": about_renderer.render,
    }

    st.sidebar.title("MachineTranslation", anchor="center")

    selection = st.sidebar.radio("Go to", list(PAGES.keys()))

    if selection is None:
        selection = "Booking"

    page = PAGES[selection]
    page(state)


if __name__ == "__main__":
    st.set_page_config(page_title="MachineTranslation", layout="wide")
    main()
