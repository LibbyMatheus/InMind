import streamlit as st
import wikipedia
import time

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(
    page_title="🧠 InMind",
    page_icon="🧠",
    layout="centered"
)

# ---------------------------
# Session State Initialization
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "last_wiki" not in st.session_state:
    st.session_state.last_wiki = None

# ---------------------------
# FAQ Buttons and Mapping
# ---------------------------
faq_buttons = [
    ("What causes dementia?", "Dementia"),
    ("What are the early signs of Alzheimer’s?", "Alzheimer's disease"),
    ("How can stroke affect memory?", "Stroke"),
    ("What are the symptoms of Parkinson’s?", "Parkinson's disease"),
]

# ---------------------------
# Wikipedia Fetch Function
# ---------------------------
@st.cache_data(show_spinner=False)
def fetch_wikipedia_summary(topic: str, max_chars: int = 900):
    """
    Fetches a Wikipedia summary with broad definitions and next steps guidance.
    """
    try:
        broad_topics = {
            "dementia": "Dementia",
            "alzheimer": "Alzheimer's disease",
            "stroke": "Stroke",
            "parkinson": "Parkinson's disease",
            "memory loss": "Amnesia",
        }

        # Use broad topic if available
        page_title = broad_topics.get(topic.lower(), topic)
        page_obj = wikipedia.page(page_title, auto_suggest=False)
        summary = wikipedia.summary(page_obj.title, sentences=3)

        if len(summary) > max_chars:
            summary = summary[:max_chars].rsplit(".", 1)[0] + "..."

        next_steps = "\n\n**Next steps:** If you or someone you know is experiencing these symptoms, consult a healthcare professional. Early detection and management are important."
        return {
            "title": page_obj.title,
            "summary": summary + next_steps,
            "url": page_obj.url
        }
    except Exception:
        return {
            "title": topic,
            "summary": "Sorry, I couldn’t find information on that. Please try another term or consult a healthcare professional.",
            "url": ""
        }

# ---------------------------
# Custom Logo Text
# ---------------------------
logo_html = """
<div style='text-align:center; font-family: "Hiragino Mincho Pro N", serif; font-size:64px; font-weight:bold;'>
    InMind.
</div>
"""
st.markdown(logo_html, unsafe_allow_html=True)

# ---------------------------
# FAQ Section
# ---------------------------
st.subheader("Common Questions")
faq_col1, faq_col2 = st.columns(2)
for i, (label, topic) in enumerate(faq_buttons):
    clicked = False
    if i % 2 == 0:
        clicked = faq_col1.button(label)
    else:
        clicked = faq_col2.button(label)

    if clicked:
        with st.spinner("Fetching answer..."):
            time.sleep(0.3)
            wiki = fetch_wikipedia_summary(topic)
        st.session_state.messages.append(("assistant", wiki["summary"]))
        st.session_state.last_wiki = wiki

# ---------------------------
# Chat Input
# ---------------------------
user_input = st.chat_input("Ask about brain health or describe symptoms...")
if user_input:
    st.session_state.messages.append(("user", user_input))
    with st.spinner("Fetching answer..."):
        time.sleep(0.3)
        wiki = fetch_wikipedia_summary(user_input)
    st.session_state.messages.append(("assistant", wiki["summary"]))
    st.session_state.last_wiki = wiki

# ---------------------------
# Chat Display
# ---------------------------
for role, msg in st.session_state.messages:
    if role == "user":
        st.chat_message("user").write(msg)
    else:
        st.chat_message("assistant").write(msg)

# ---------------------------
# Favorites and Clear Buttons
# ---------------------------
btn_col1, btn_col2 = st.columns(2)
if btn_col1.button("⭐ Favorite"):
    if st.session_state.last_wiki and st.session_state.last_wiki not in st.session_state.favorites:
        st.session_state.favorites.append(st.session_state.last_wiki)

if btn_col2.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.session_state.last_wiki = None
    st.session_state.favorites = []
    st.experimental_rerun()

# ---------------------------
# Favorites Display
# ---------------------------
if st.session_state.favorites:
    st.subheader("⭐ Favorites")
    for fav in st.session_state.favorites:
        if fav["url"]:
            st.markdown(f"**[{fav['title']}]({fav['url']})** - {fav['summary']}")
        else:
            st.markdown(f"**{fav['title']}** - {fav['summary']}")
