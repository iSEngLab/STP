import streamlit as st
from app.common import State


def render(state: State) -> None:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.title("About us")
        st.write(
            """
            We are a group of students from the University of Bucharest.
            We are passionate about machine learning and natural language processing.
            """
        )
        st.write(
            """
            Team members:
            - :boy: Liviu Sopon (:link: https://www.linkedin.com/in/liviu-sopon)
            - :girl: Raluca Tudor (:link: https://www.linkedin.com/in/raluca-tudor)
            - :boy: Ioachim Lihor (:link: https://www.linkedin.com/in/ioachim-lihor-61b528187/)
            """
        )
