import streamlit as st

from ui import (
    angler_perf,
    avg_winning_wt,
    avg_winning_wt_lake,
    top_twenty,
    winning_wt_lake,
)


def main():
    st.set_page_config(layout="wide")
    st.title("BASS CHAMPS Tournament Data")

    for section in [
        avg_winning_wt.show,
        avg_winning_wt_lake.show,
        winning_wt_lake.show,
        top_twenty.show,
        angler_perf.show,
    ]:
        section()


if __name__ == "__main__":
    main()
