import os, pandas as pd, plotly.express as px, streamlit as st
from supabase import create_client
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Dallas Cowboys — Seasons", layout="wide")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME = os.getenv("TABLE_NAME", "cowboys_seasons")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Missing SUPABASE_URL or SUPABASE_KEY env vars.")
    st.stop()

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

@st.cache_data(ttl=60)
def fetch_data():
    data = sb.table(TABLE_NAME).select("*").order("season", desc=True).limit(500).execute()
    items = data.data or []
    df = pd.DataFrame(items)
    return df

st.title("Dallas Cowboys — Season Dashboard")

df = fetch_data()
if df.empty:
    st.info("No data yet. Run the collector → structurer → loader.")
    st.stop()

df = df.sort_values("season")
df["games"] = df["wins"].fillna(0) + df["losses"].fillna(0) + df["ties"].fillna(0)
df["win_pct"] = (df["wins"] / df["games"]).where(df["games"] > 0, 0)

st.subheader("Seasons Table")
st.dataframe(df.iloc[::-1], use_container_width=True)

c1, c2 = st.columns(2)

with c1:
    if {"season","wins"}.issubset(df.columns):
        fig = px.line(df, x="season", y="wins", title="Wins by Season")
        st.plotly_chart(fig, use_container_width=True)

with c2:
    if {"season","points_for","points_against"}.issubset(df.columns):
        fig2 = px.scatter(
            df, x="points_against", y="points_for",
            hover_name="season", title="Points For vs Points Against"
        )
        st.plotly_chart(fig2, use_container_width=True)

if "playoffs" in df.columns:
    pl = df["playoffs"].fillna("Unknown").value_counts().reset_index()
    pl.columns = ["playoffs_result","count"]
    fig3 = px.bar(pl, x="playoffs_result", y="count", title="Playoff Results (Counts)")
    st.plotly_chart(fig3, use_container_width=True)
