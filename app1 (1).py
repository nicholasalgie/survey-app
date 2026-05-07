import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from supabase import create_client

NAMES = [
    "Alberto", "Alice", "Andres", "Caterina", "Cecilia", "Chiara", "Claudio",
    "Danny", "Edoardo", "Elisa B.", "Elisa E.", "Enrico", "Federico", "Filippo", "Gabriele",
    "Giulia R.", "Giulia D.", "Grace", "Inelda", "Irene", "Leonardo",
    "Luca Te.", "Luca Tr.", "Ludovica", "Nader", "Nicholas", "Roberto", "Simone",
    "Tommaso", "Valentina", "Veronica", "Hazal", "Marta", "Andrea"
]

QUESTION = "How well does the presentation reflect the purpose of Tiresia/Triadi?"

@st.cache_resource
def get_client():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def save_response(presented_by, score):
    get_client().table("responses").insert({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "presented_by": presented_by,
        "score": score
    }).execute()

def get_all_stats():
    result = get_client().table("responses").select("presented_by, score").execute()
    return pd.DataFrame(result.data) if result.data else pd.DataFrame(columns=["presented_by", "score"])

# --- Init session state ---
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# --- Page config ---
st.set_page_config(page_title="Presentation Survey", page_icon="🎯", layout="centered")

# --- Finished screen ---
if st.session_state.current_index >= len(NAMES):
    st.title("🎉 All done! Thank you!")
    st.divider()

    df = get_all_stats()
    if not df.empty:
        st.subheader("📊 Overall Results")

        # Top scorer
        avg_by_person = df.groupby("presented_by")["score"].mean()
        top_name = avg_by_person.idxmax()
        top_score = avg_by_person.max()
        st.success(f"🏆 Highest rated: **{top_name}** with an average of **{top_score:.2f} / 5**")

        # Overall metrics
        col1, col2 = st.columns(2)
        col1.metric("Total ratings", len(df))
        col2.metric("Overall average", f"{df['score'].mean():.2f} / 5")

        # Distribution of all scores
        st.write("**Score distribution (all presenters)**")
        counts = df["score"].value_counts().reindex(range(6), fill_value=0)
        fig, ax = plt.subplots(figsize=(6, 3))
        bars = ax.bar(counts.index, counts.values, color="#4A90D9", edgecolor="white", width=0.6)
        ax.set_xticks(range(6))
        ax.set_xlabel("Score")
        ax.set_ylabel("Number of ratings")
        ax.set_facecolor("#f9f9f9")
        fig.patch.set_facecolor("#f9f9f9")
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, h + 0.05,
                        str(int(h)), ha="center", va="bottom", fontsize=9)
        plt.tight_layout()
        st.pyplot(fig)

    if st.button("⬅️ Go back"):
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

# --- Rating ---
if not st.session_state.submitted:
    score = st.slider("Your rating", 0, 5, 3)
    if st.button("✅ Submit rating", type="primary", use_container_width=True):
        save_response(current_name, score)
        st.session_state.submitted = True
        st.rerun()

else:
    st.success("✅ Submitted! Move to the next presenter.")
    st.divider()

    col_back, col_next = st.columns(2)
    with col_back:
        if st.session_state.current_index > 0:
            if st.button("⬅️ Previous", use_container_width=True):
                st.session_state.current_index -= 1
                st.session_state.submitted = True
                st.rerun()
    with col_next:
        label = "➡️ Next presenter" if st.session_state.current_index < len(NAMES) - 1 else "🎉 Finish"
        if st.button(label, type="primary", use_container_width=True):
            st.session_state.current_index += 1
            st.session_state.submitted = False
            st.rerun()
