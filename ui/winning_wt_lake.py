from sqlite3 import Connection

import altair as alt
import pandas as pd
import streamlit as st

from constants import PLACES
from db import db_conn, load_data


@db_conn
def show(c: Connection) -> None:
    st.header("🏆Winning Weights by Lake per Year")
    df = (
        load_data(c, q_file="queries/wt_lake_year.sql")
        .pivot(index=["year", "lake"], columns="place", values="weight")
        .fillna(0)
        .reset_index()
    )
    rows = []
    for _, r in df.iterrows():
        y, lake = r["year"], r["lake"]
        p = {1: r.get(1, 0), 2: r.get(2, 0), 3: r.get(3, 0)}
        base = 0
        for place, emoji in zip([3, 2, 1], PLACES[::-1]):
            height = p[place]
            rows.append(
                {
                    "year": y,
                    "lake": lake,
                    "place": emoji,
                    "weight": height,
                    "label_y": base + height / 2,
                    "label": f"{height:.2f}",
                    "weight_lbs": f"{height:.2f} lbs",
                }
            )
            base += height

    df_label = pd.DataFrame(rows)
    df_label["place"] = pd.Categorical(
        df_label["place"], categories=PLACES, ordered=True
    )

    years = sorted(df_label["year"].unique(), reverse=True)
    tabs = st.tabs(years)
    for idx, year in enumerate(years):
        with tabs[idx]:
            df_year = df_label[df_label["year"] == year]
            bars = (
                alt.Chart(df_year)
                .mark_bar()
                .encode(
                    x=alt.X(
                        "lake:N",
                        title="Lake",
                        sort="-y",
                        axis=alt.Axis(
                            labelFontSize=10, labelLimit=0, labelFontStyle="bold"
                        ),
                    ),
                    y=alt.Y("weight:Q", title="Weight(lbs)", stack="zero"),
                    color=alt.Color(
                        "place:N",
                        sort=PLACES,
                        scale=alt.Scale(scheme="blues"),
                        title="Place",
                    ),
                    tooltip=[
                        alt.Tooltip("lake:N", title="Lake"),
                        alt.Tooltip("place:N", title="Place"),
                        alt.Tooltip("weight_lbs:N", title="Weight"),
                    ],
                )
            )
            labels = (
                alt.Chart(df_year)
                .mark_text(
                    align="center",
                    baseline="middle",
                    color="white",
                    fontSize=11,
                    fontStyle="bold",
                    tooltip=None,
                )
                .encode(x="lake:N", y="label_y:Q", text="label:N")
            )

            st.altair_chart((bars + labels).properties(height=425), use_container_width=True)
