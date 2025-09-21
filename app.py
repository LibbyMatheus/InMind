import streamlit as st
import wikipedia

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(
    page_title="🧠 InMind",
    page_icon="🧠",
    layout="centered"
)

# ---------------------------
# Initialize Session State
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "last_wiki" not in st.session_state:
    st.session_state.last_wiki = None

# ---------------------------
# FAQ Section
# ---------------------------
faq_buttons = [
    ("What causes dementia?", "dementia"),
    ("What are the early signs of Alzheimer’s?", "alzheimer"),
    ("How can stroke affect memory?", "stroke"),
    ("What are the symptoms of Parkinson’s?", "parkinson"),
]

# ---------------------------
# Caching Helper
# ---------------------------
@st.cache_data(show_spinner=False)
def cached_wikipedia_query(prompt: str, topic_key: str = None, max_chars: int = 900):
    try:
        canonical_topics = {
            "dementia": "Dementia",
            "alzheimer": "Alzheimer's disease",
            "stroke": "Stroke",
            "parkinson": "Parkinson's disease",
            "memory loss": "Amnesia",
        }

        if topic_key and topic_key in canonical_topics:
            page_name = canonical_topics[topic_key]
            page_obj = wikipedia.page(page_name, auto_suggest=False)
            summary = wikipedia.summary(page_obj.title, sentences=3)
        else:
            results = wikipedia.search(prompt, results=3)
            if not results:
                return None
            page_obj = wikipedia.page(results[0], auto_suggest=False)
            summary = wikipedia.summary(page_obj.title, sentences=3)

        if len(summary) > max_chars:
            summary = summary[:max_chars].rsplit(".", 1)[0] + "..."
        return {
            "title": page_obj.title,
            "summary": summary,
            "url": page_obj.url
        }
    except Exception:
        return None

# ---------------------------
# Header with Logo only
# ---------------------------
st.image("LOGO_PATH.png", width=120)  # replace LOGO_PATH.png with your logo path or URL
# Optional subtitle:
# st.write("Your companion for brain health resources.")

# ---------------------------
# FAQ Section
# ---------------------------
st.subheader("Common Questions")
faq_col1, faq_col2 = st.columns(2)
for i, (label, topic_key) in enumerate(faq_buttons):
    if i % 2 == 0:
        if faq_col1.button(label):
            wiki = cached_wikipedia_query(label, topic_key=topic_key)
            if wiki:
                st.session_state.messages.append(("assistant", wiki["summary"]))
                st.session_state.last_wiki = wiki
    else:
        if faq_col2.button(label):
            wiki = cached_wikipedia_query(label, topic_key=topic_key)
            if wiki:
                st.session_state.messages.append(("assistant", wiki["summary"]))
                st.session_state.last_wiki = wiki

# ---------------------------
# Chat Input
# ---------------------------
user_input = st.chat_input("Ask about brain health...")
if user_input:
    st.session_state.messages.append(("user", user_input))
    wiki = cached_wikipedia_query(user_input)
    if wiki:
        st.session_state.messages.append(("assistant", wiki["summary"]))
        st.session_state.last_wiki = wiki
    else:
        st.session_state.messages.append(("assistant", "Sorry, I couldn’t find information on that."))

# ---------------------------
# Chat Display
# ---------------------------
for role, msg in st.session_state.messages:
    if role == "user":
        st.chat_message("user").write(msg)
    else:
        st.chat_message("assistant").write(msg)

# ---------------------------
# Buttons (Favorites, Clear)
# ---------------------------
btn_col1, btn_col2 = st.columns(2)
if btn_col1.button("⭐ Favorite"):
    if st.session_state.last_wiki and st.session_state.last_wiki not in st.session_state.favorites:
        st.session_state.favorites.append(st.session_state.last_wiki)

if btn_col2.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.session_state.last_wiki = None
    st.session_state.favorites = []
    st.rerun()

# ---------------------------
# Favorites Display
# ---------------------------
if st.session_state.favorites:
    st.subheader("⭐ Favorites")
    for fav in st.session_state.favorites:
        st.markdown(f"**[{fav['title']}]({fav['url']})** - {fav['summary']}")
