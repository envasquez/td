from sqlite3 import Connection

import altair as alt
import pandas as pd
import streamlit as st

from db import db_conn, load_data, load_query


@db_conn
def show(c: Connection) -> None:
    st.title("Angler Performance Viewer")
    angler_list = (
        load_data(c, q_file="queries/all_anglers.sql")["angler"]
        .dropna()
        .sort_values()
        .unique()
        .tolist()
    )
    selected_angler = st.text_input(
        "Search for Angler Name", "", placeholder="Type angler name ..."
    )
    if any([not selected_angler, selected_angler not in angler_list]):
        st.warning("No close match found ...")
        st.stop()
    st.success(f"Showing results for: **{selected_angler}**")

    df = pd.read_sql(
        load_query(filename="queries/angler_performance.sql"),
        c,
        params=(selected_angler, selected_angler),
    )
    if df.empty:
        st.info("No tournament data found for that angler.")
        st.stop()

    st.subheader("Finishes [best, then most recent]")
    st.dataframe(
        df[["place", "lake", "weight", "fish", "date"]],
        use_container_width=True,
        hide_index=True,
    )
    df["year"] = pd.to_datetime(df["date"]).dt.year
    yearly_stats = (
        df.groupby("year")
        .agg(avg_weight=("weight", "mean"), avg_place=("place", "mean"))
        .reset_index()
    )
    st.subheader("📈 Yearly Average Stats")
    c1, c2 = st.columns(2)
    weight_chart = alt.Chart(yearly_stats).mark_line(
        point=True, color="#4e79a7"
    ).encode(
        x=alt.X("year:O", title="Year"),
        y=alt.Y("avg_weight:Q", title="Avg Weight", scale=alt.Scale(zero=False)),
        tooltip=["year", "avg_weight"],
    ) + alt.Chart(yearly_stats).mark_text(
        align="center", baseline="bottom", dy=-5, color="#4e79a7"
    ).encode(x="year:O", y="avg_weight:Q", text=alt.Text("avg_weight:Q", format=".1f"))
    place_chart = alt.Chart(yearly_stats).mark_line(point=True, color="#f28e2b").encode(
        x=alt.X("year:O", title="Year"),
        y=alt.Y(
            "avg_place:Q",
            title="Avg Place (lower is better)",
            scale=alt.Scale(reverse=True),
        ),
        tooltip=["year", "avg_place"],
    ) + alt.Chart(yearly_stats).mark_text(
        align="center", baseline="bottom", dy=-5, color="#f28e2b"
    ).encode(x="year:O", y="avg_place:Q", text=alt.Text("avg_place:Q", format=".1f"))
    c1.altair_chart(weight_chart, use_container_width=True)
    c2.altair_chart(place_chart, use_container_width=True)
