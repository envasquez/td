from sqlite3 import Connection

import altair as alt
import pandas as pd
import streamlit as st
import unicodedata
import string

from db import db_conn, load_data, load_query


def normalize_name(name: str) -> str:
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    name = name.lower().translate(str.maketrans("", "", string.punctuation))
    parts = name.split()
    if len(parts) == 3 and len(parts[1]) == 1:  # Remove middle initial
        parts.pop(1)
    return " ".join(parts)


@db_conn
def show(c: Connection) -> None:
    st.title("Angler Performance Viewer")
    anglers_df = load_data(c, q_file="queries/all_anglers.sql")
    anglers_df = anglers_df.dropna().drop_duplicates().sort_values(by="angler")
    anglers_df["norm"] = anglers_df["angler"].map(normalize_name)

    selected_angler_raw = st.text_input(
        "Search for Angler Name", "", placeholder="Type angler name ..."
    )
    if not selected_angler_raw:
        st.stop()

    normalized_input = normalize_name(selected_angler_raw)
    matches = anglers_df[anglers_df["norm"] == normalized_input]["angler"].tolist()
    if not matches:
        st.warning("No close match found ...")
        st.stop()
    elif len(matches) > 1:
        chosen = st.selectbox("Multiple matches found. Please select one:", matches)
        angler = chosen
    else:
        angler = matches[0]
    st.success(f"Showing results for: **{angler}**")

    df = pd.read_sql(
        load_query(filename="queries/angler_performance.sql"),
        c,
        params=(angler, angler),
    )
    if df.empty:
        st.info("No tournament data found for that angler.")
        st.stop()

    st.subheader("Finishes [best, then most recent]")
    column_config = {
        "place": st.column_config.NumberColumn("Place", width="small"),
        "lake": st.column_config.TextColumn("Lake", width="small"),
        "weight": st.column_config.NumberColumn("Weight(lbs)", width="small"),
        "fish": st.column_config.NumberColumn("# Fish", width="small"),
        "big_bass": st.column_config.NumberColumn("BigBass(lbs)", width="small"),
        "date": st.column_config.TextColumn("Date", width="small"),
        "prize": st.column_config.TextColumn("Prize", width="large"),
    }
    st.data_editor(
        df[["place", "lake", "weight", "fish", "big_bass", "date", "prize"]],
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
        disabled=True,
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

