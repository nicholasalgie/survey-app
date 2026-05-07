import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from sqlalchemy import text

NAMES = [
    "Alberto", "Alice", "Andres", "Caterina", "Cecilia", "Chiara", "Claudio",
    "Danny", "Edoardo", "Elisa B.", "Elisa E.", "Enrico", "Federico", "Filippo", "Gabriele",
    "Giulia R.", "Giulia D.", "Grace", "Inelda", "Irene", "Leonardo",
    "Luca Te.", "Luca Tr.", "Ludovica", "Mario", "Nader", "Nicholas", "Roberto", "Simone",
    "Tommaso", "Valentina", "Veronica", "Hazal", "Marta", "Andrea"
]

QUESTION = "How well does the presentation reflect the purpose of Tiresia/Triadi?"

# --- Database setup ---
conn = st.connection("survey_db", type="sql", url="sqlite:///survey.db")

with conn.session as s:
    s.execute(text("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            presented_by TEXT,
            score INTEGER
        )
    """))
    s.commit()

def save_response(presented_by, score):
    with conn.session as s:
        s.execute(
            text("INSERT INTO responses (timestamp, presented_by, score) VALUES (:ts, :name, :score)"),
            {"ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "name": presented_by, "score": score}
        )
        s.commit()

def get_stats(name):
    return conn.query(
        "SELECT score FROM responses WHERE presented_by = :name",
        params={"name": name}, ttl=0
    )

# --- Init session state ---
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# --- Page config ---
st.set_page_config(page_title="Presentation Survey", page_icon="🎯", layout="centered")

# --- Finished ---
if st.session_state.current_index >= len(NAMES):
    st.title("🎉 All done!")
    st.success("You have rated all presenters. Thank you!")
    if st.button("⬅️ Go back to last presenter"):
        st.session_state.current_index = len(NAMES) - 1
        st.session_state.submitted = True
        st.rerun()
    st.stop()

current_name = NAMES[st.session_state.current_index]

# --- Header ---
st.progress(st.session_state.current_index / len(NAMES))
st.caption(f"Presenter {st.session_state.current_index + 1} of {len(NAMES)}")
st.title(f"🎤 {current_name}")
st.write(f"*{QUESTION}*")
st.divider()

# --- Rating or Stats ---
if not st.session_state.submitted:
    score = st.slider("Your rating", 0, 5, 3)
    if st.button("✅ Submit rating", type="primary", use_container_width=True):
        save_response(current_name, score)
        st.session_state.submitted = True
        st.rerun()

else:
    st.success("✅ Rating submitted!")
    subset = get_stats(current_name)

    if not subset.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Responses", len(subset))
        col2.metric("Average", f"{subset['score'].mean():.2f} / 5")
        col3.metric("Most common", int(subset['score'].mode()[0]))

        counts = subset["score"].value_counts().reindex(range(6), fill_value=0)
        fig, ax = plt.subplots(figsize=(6, 3))
        bars = ax.bar(counts.index, counts.values, color="#4A90D9", edgecolor="white", width=0.6)
        ax.set_xticks(range(6))
        ax.set_xlabel("Score")
        ax.set_ylabel("Responses")
        ax.set_facecolor("#f9f9f9")
        fig.patch.set_facecolor("#f9f9f9")
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, h + 0.05,
                        str(int(h)), ha="center", va="bottom", fontsize=9)
        plt.tight_layout()
        st.pyplot(fig)

    st.divider()

# --- Navigation ---
col_back, col_next = st.columns(2)

with col_back:
    if st.session_state.current_index > 0:
        if st.button("⬅️ Previous", use_container_width=True):
            st.session_state.current_index -= 1
            st.session_state.submitted = True
            st.rerun()

with col_next:
    if st.session_state.submitted:
        label = "➡️ Next presenter" if st.session_state.current_index < len(NAMES) - 1 else "🎉 Finish"
        if st.button(label, type="primary", use_container_width=True):
            st.session_state.current_index += 1
            st.session_state.submitted = False
            st.rerun()
