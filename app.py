import sqlite3

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

TEXT_COLOR = "white" if st.get_option("theme.base") in ["dark", None] else "black"


conn = sqlite3.connect("tournaments.db")

st.header("BASS CHAMPS Tournament Data")
#
# Average Winning Weight by Lake
#
st.title("🎣Average Winning Weight Per Year")
avg_winning_wts = """
    SELECT
        strftime('%Y', t.date) AS year,
        ROUND(AVG(r.weight), 2) AS avg_winning_weight
    FROM results r
    JOIN tournaments t ON r.tournament_id = t.id
    WHERE r.place = 1 AND r.weight IS NOT NULL AND t.lake IN (
        SELECT lake
        FROM tournaments
        GROUP BY lake
        HAVING COUNT(*) != 1
    )
    GROUP BY year
    ORDER BY year;
"""
df = pd.read_sql_query(avg_winning_wts, conn)
bars = (
    alt.Chart(df)
    .mark_bar(color="steelblue")
    .encode(
        x=alt.X("year:N", title="Year", sort=None),
        y=alt.Y("avg_winning_weight:Q", title="Avg Winning Weight (lbs)"),
        tooltip=["year:N", "avg_winning_weight:Q"],
    )
)
text = (
    alt.Chart(df)
    .mark_text(
        align="center",
        baseline="bottom",
        dy=-5,
        color=TEXT_COLOR,
        fontSize=12,
        fontStyle="bold",
    )
    .encode(x="year:N", y="avg_winning_weight:Q", text="avg_winning_weight:Q")
)
st.altair_chart(bars + text, use_container_width=True)
#
# Average Winning Weight by Lake
#
st.title("Average Winning Weight & Frequency per Lake")
avg_winning_wts_by_lake = """
SELECT
    t.lake,
    COUNT(*) AS tournament_count,
    ROUND(AVG(r.weight), 2) AS avg_winning_weight
FROM tournaments t
JOIN results r ON t.id = r.tournament_id
WHERE r.place = 1 AND t.lake IS NOT NULL
GROUP BY t.lake
"""
df = pd.read_sql_query(avg_winning_wts_by_lake, conn)
df = df.sort_values("avg_winning_weight", ascending=False).reset_index(drop=True)
df["lake"] = pd.Categorical(df["lake"], categories=df["lake"], ordered=True)
max_count = df["tournament_count"].max()
base = alt.Chart(df).encode(x=alt.X("lake:N", title="Lake", sort=None))
text = base.mark_text(
    align="center", baseline="bottom", dy=-5, color=TEXT_COLOR, fontSize=12
).encode(
    y=alt.Y("avg_winning_weight:Q", axis=alt.Axis(title=None)),
    text=alt.Text("avg_winning_weight:Q", format=".2f"),
)
bars = base.mark_bar(color="steelblue").encode(
    y=alt.Y("avg_winning_weight:Q", axis=alt.Axis(title=None)),
    tooltip=["lake", "avg_winning_weight", "tournament_count"],
)
line = base.mark_line(interpolate="monotone", color="orange", strokeWidth=2).encode(
    y=alt.Y(
        "tournament_count:Q",
        axis=alt.Axis(title="Tournament Count"),
        scale=alt.Scale(domain=(1, max_count + 1)),
    ),
    tooltip=["lake", "avg_winning_weight", "tournament_count"],
)
chart = (
    alt.layer(bars, line, text).resolve_scale(y="independent").properties(height=500)
)
st.altair_chart(chart, use_container_width=True)
#
# Top Ten Finishers by Year by Tournament
#
st.title("Top 10 Finishers by Tournament")
tournaments_df = pd.read_sql(
    "SELECT id, tournament, date FROM tournaments ORDER BY date DESC", conn
)
tournaments_df["year"] = pd.to_datetime(tournaments_df["date"]).dt.year
years = sorted(tournaments_df["year"].unique(), reverse=True)
tab_objs = st.tabs([str(year) for year in years])
for i, year in enumerate(years):
    with tab_objs[i]:
        tournaments_in_year = tournaments_df[tournaments_df["year"] == year].copy()
        tournaments_in_year["label"] = (
            tournaments_in_year["tournament"] + " (" + tournaments_in_year["date"] + ")"
        )
        tournament_map = dict(
            zip(tournaments_in_year["label"], tournaments_in_year["id"])
        )
        selected_label = st.selectbox(
            "Select a Tournament", list(tournament_map.keys()), key=f"select_{year}"
        )
        selected_id = tournament_map[selected_label]
        results_df = pd.read_sql(
            """
            SELECT
                place,
                angler1,
                angler1_hometown,
                angler2,
                angler2_hometown,
                fish,
                big_bass,
                weight
            FROM results
            WHERE tournament_id = ?
            ORDER BY place ASC
            LIMIT 10
            """,
            conn,
            params=(selected_id,),
        )
        st.subheader("Top 10 Results")
        st.dataframe(results_df, use_container_width=True)
#
# Angler Search & Perfomance
#
st.title("Angler Performance Viewer")
angler_query = """
SELECT DISTINCT angler FROM (
    SELECT angler1 AS angler FROM results
    UNION
    SELECT angler2 AS angler FROM results
) WHERE angler IS NOT NULL AND angler != ''
ORDER BY angler
"""
angler_list = (
    pd.read_sql(angler_query, conn)["angler"].dropna().sort_values().unique().tolist()
)
selected_angler = st.text_input(
    "Search for Angler Name", "", placeholder="Type angler name..."
)
if not selected_angler:
    st.stop()
if selected_angler not in angler_list:
    st.warning("Angler not found. Try typing a full name or check spelling.")
    st.stop()
query = """
SELECT
    t.date,
    strftime('%Y', t.date) AS year,
    t.lake,
    r.place,
    r.weight,
    r.fish
FROM tournaments t
JOIN results r ON t.id = r.tournament_id
WHERE r.angler1 = ? OR r.angler2 = ?
ORDER BY r.place ASC, t.date DESC
"""
df = pd.read_sql(query, conn, params=(selected_angler, selected_angler))
if df.empty:
    st.info("No tournament data found for that angler.")
    st.stop()
st.subheader("🏆 Finishes (Best First, Then Most Recent)")
st.dataframe(df[["place", "lake", "weight", "fish", "date"]], use_container_width=True)
df["year"] = pd.to_datetime(df["date"]).dt.year
yearly_stats = (
    df.groupby("year")
    .agg(avg_weight=("weight", "mean"), avg_place=("place", "mean"))
    .reset_index()
)
st.subheader("📈 Yearly Average Stats")
c1, c2 = st.columns(2)
weight_chart = alt.Chart(yearly_stats).mark_line(point=True, color="#4e79a7").encode(
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
        title="Avg Place (Lower is Better)",
        scale=alt.Scale(reverse=True),
    ),
    tooltip=["year", "avg_place"],
) + alt.Chart(yearly_stats).mark_text(
    align="center", baseline="bottom", dy=-5, color="#f28e2b"
).encode(x="year:O", y="avg_place:Q", text=alt.Text("avg_place:Q", format=".1f"))
c1.altair_chart(weight_chart, use_container_width=True)
c2.altair_chart(place_chart, use_container_width=True)


# Done!
conn.close()
