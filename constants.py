import streamlit as st

PLACES = ["🥇 1st", "🥈 2nd", "🥉 3rd"]
TEXT_COLOR = "white" if st.get_option("theme.base") in ["dark", None] else "grey"
