import streamlit as st
import wikipedia

# Page config
st.set_page_config(page_title="InMind", layout="wide")

# --- Centered Logo ---
LOGO_PATH = "LOGO_PATH.png"
st.markdown(
    f"""
    <div style="display: flex; justify-content: center; margin-bottom: 20px;">
        <img src="app://{LOGO_PATH}" alt="InMind Logo" style="max-width: 300px;">
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Sidebar FAQs ---
st.sidebar.title("Common Questions")
faq_questions = [
    "What is dementia?",
    "What is Alzheimer's disease?",
    "What are early symptoms of dementia?",
    "What is Parkinson's disease?",
    "What are prevention methods for Alzheimer's?"
]
faq_choice = st.sidebar.radio("Select a question:", faq_questions, index=None)

# --- Chat storage ---
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# --- Wikipedia Search (medical/science focus) ---
def search_wikipedia(query):
    try:
        # Search Wikipedia
        results = wikipedia.search(query)
        if not results:
            return None

        # Prefer medical/scientific topics
        for result in results:
            if any(keyword in result.lower() for keyword in ["disease", "syndrome", "medicine", "disorder", "health", "neuro", "condition"]):
                return wikipedia.summary(result, sentences=3, auto_suggest=False, redirect=True)

        # Fallback: first result
        return wikipedia.summary(results[0], sentences=3, auto_suggest=False, redirect=True)
    except Exception:
        return None

# --- Handle FAQ selection ---
if faq_choice:
    answer = search_wikipedia(faq_choice)
    if answer:
        st.session_state["messages"].append(("user", faq_choice))
        st.session_state["messages"].append(("bot", answer))
    else:
        st.session_state["messages"].append(("user", faq_choice))
        st.session_state["messages"].append(("bot", "Sorry, I couldn’t find a medical or scientific answer for that."))

# --- Chat input ---
user_input = st.chat_input("Ask InMind about symptoms, conditions, or prevention...")
if user_input:
    answer = search_wikipedia(user_input)
    if answer:
        st.session_state["messages"].append(("user", user_input))
        st.session_state["messages"].append(("bot", answer))
    else:
        st.session_state["messages"].append(("user", user_input))
        st.session_state["messages"].append(("bot", "Sorry, I couldn’t find a medical or scientific answer for that."))

# --- Display messages ---
for sender, message in st.session_state["messages"]:
    if sender == "user":
        st.chat_message("user").write(message)
    else:
        st.chat_message("assistant").write(message)

# --- Clear Chat Button ---
if st.button("Clear Chat"):
    st.session_state["messages"] = []
    st.rerun()

# --- Disclaimer ---
st.markdown(
    """
    <div style="text-align: center; margin-top: 30px; font-size: 13px; color: gray;">
        Disclaimer: InMind is not a substitute for professional medical advice. Always consult a healthcare provider for serious concerns.
    </div>
    """,
    unsafe_allow_html=True,
)
