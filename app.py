import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

st.set_page_config(page_title="COVID-19 Data Explorer", layout="wide")

# ✅ Only load the columns we actually use
USE_COLS = ["title", "abstract", "publish_time", "journal", "source_x"]

@st.cache_data
def load_data(sample=False):
    file_path = os.path.join(os.path.dirname(__file__), "data", "metadata.csv")
    if not os.path.exists(file_path):
        st.error("❌ Could not find `metadata.csv` in the `data/` folder.")
        return None

    # For development, load a sample to speed things up
    if sample:
        df = pd.read_csv(file_path, usecols=USE_COLS, nrows=5000)
    else:
        df = pd.read_csv(file_path, usecols=USE_COLS)

    # Clean and prepare
    df['publish_time'] = pd.to_datetime(df['publish_time'], errors='coerce')
    df['year'] = df['publish_time'].dt.year
    df['abstract_word_count'] = df['abstract'].fillna("").apply(lambda x: len(x.split()))
    return df

# Sidebar option to use sample data
use_sample = st.sidebar.checkbox("Use sample data for faster loading", value=True)
df = load_data(sample=use_sample)

if df is None or df.empty:
    st.warning("⚠️ No data available to display.")
else:
    st.title("📊 COVID-19 Data Explorer")
    st.write("Interactive exploration of COVID-19 research papers from the CORD-19 dataset.")

    # --- Dataset Summary ---
st.subheader("📌 Dataset Summary")
total_papers = len(df)
total_journals = df['journal'].nunique()
min_date = df['publish_time'].min()
max_date = df['publish_time'].max()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Papers", f"{total_papers:,}")
col2.metric("Unique Journals", f"{total_journals:,}")
col3.metric(
            "Earliest Publication",
            min_date.strftime("%Y-%m-%d") if pd.notnull(min_date) else "N/A"
        )
col4.metric(
            "Latest Publication",
            max_date.strftime("%Y-%m-%d") if pd.notnull(max_date) else "N/A"
        )

st.markdown("---")

    # --- Filters ---
min_year = int(df['year'].min()) if pd.notnull(df['year'].min()) else 2019
max_year = int(df['year'].max()) if pd.notnull(df['year'].max()) else 2022
year_range = st.sidebar.slider("Select year range", min_year, max_year, (min_year, max_year))

filtered_df = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]

if filtered_df.empty:
        st.warning("⚠️ No papers found for the selected year range.")
else:
        # Sample data preview
        st.subheader("Sample Data")
        st.dataframe(filtered_df.head())

        # Publications over time
        st.subheader("Publications Over Time")
        fig, ax = plt.subplots()
        sns.countplot(x='year', data=filtered_df, ax=ax)
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # Top journals
        st.subheader("Top Journals")
        top_journals = filtered_df['journal'].value_counts().head(10)
        fig, ax = plt.subplots()
        top_journals.plot(kind='bar', ax=ax)
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # Word cloud (on demand)
        if st.checkbox("Generate Word Cloud of Paper Titles"):
            text = " ".join(filtered_df['title'].dropna())
            if text.strip():
                wc = WordCloud(width=800, height=400, background_color='white').generate(text)
                fig, ax = plt.subplots()
                ax.imshow(wc, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
            else:
                st.info("ℹ️ No titles available to generate a word cloud.")
