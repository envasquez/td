from sqlite3 import Connection

import pandas as pd
import streamlit as st

from db import db_conn, load_query


@db_conn
def show(c: Connection) -> None:
    st.header("Top 20 Teams by Tournament")
    tournaments_df = pd.read_sql(
        "SELECT id, tournament, date FROM tournaments ORDER BY date DESC", c
    )
    tournaments_df["year"] = pd.to_datetime(tournaments_df["date"]).dt.year
    years = sorted(tournaments_df["year"].unique(), reverse=True)
    tab_objs = st.tabs([str(year) for year in years])
    for idx, year in enumerate(years):
        with tab_objs[idx]:
            tournaments_in_year = tournaments_df[tournaments_df["year"] == year].copy()
            tournaments_in_year["label"] = (
                tournaments_in_year["tournament"]
                + " ("
                + tournaments_in_year["date"]
                + ")"
            )
            tournament_map = dict(
                zip(tournaments_in_year["label"], tournaments_in_year["id"])
            )
            selected_label = st.selectbox(
                "Select a Tournament", list(tournament_map.keys()), key=f"select_{year}"
            )
            selected_id = tournament_map[selected_label]
            results_df = pd.read_sql(
                load_query(filename="queries/top_twenty.sql"), c, params=(selected_id,)
            )
            st.subheader("Top 20 Results")
            column_config = {
                "place": st.column_config.NumberColumn("Place", width="small"),
                "angler": st.column_config.TextColumn("Angler", width="medium"),
                "weight": st.column_config.NumberColumn("Weight(lbs)", width="small"),
                "big_bass": st.column_config.NumberColumn(
                    "BigBass (lbs)", width="small"
                ),
                "prize": st.column_config.TextColumn("Prize", width="large"),
            }
            st.data_editor(
                results_df,
                column_config=column_config,
                use_container_width=True,
                hide_index=True,
                disabled=True,
            )
