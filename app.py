import streamlit as st
import wikipedia
import urllib.parse
from datetime import datetime

# -----------------------------
# Canonical medical bias
# -----------------------------
CANONICAL_TOPICS = {
    "stroke": "Stroke",
    "strokes": "Stroke",
    "parkinson": "Parkinson's disease",
    "dementia": "Dementia",
    "alzheimer": "Alzheimer's disease",
    "alzheimers": "Alzheimer's disease",
    "memory loss": "Amnesia",
    "seizure": "Seizure",
    "heart attack": "Myocardial infarction"
}

# -----------------------------
# Wikipedia query
# -----------------------------
def query_wikipedia_article(prompt: str, max_chars: int = 900):
    try:
        lower_prompt = prompt.lower()

        # ✅ Bias toward medical canonical topics
        for key, page in CANONICAL_TOPICS.items():
            if key in lower_prompt:
                try:
                    page_obj = wikipedia.page(page, auto_suggest=False)
                    summary = wikipedia.summary(page_obj.title, sentences=3)
                    if len(summary) > max_chars:
                        summary = summary[:max_chars].rsplit(".", 1)[0] + "..."
                    return {
                        "title": page_obj.title,
                        "summary": summary,
                        "url": page_obj.url
                    }
                except Exception:
                    pass  # fallback

        # ✅ Normal Wikipedia search
        results = wikipedia.search(prompt, results=3)
        if not results:
            return None

        title = results[0]

        # ✅ Avoid irrelevant niche subtypes unless user asked
        if any(word in title.lower() for word in ["childhood", "variant", "subtype", "familial"]):
            for candidate in results[1:]:
                if not any(w in candidate.lower() for w in ["childhood", "variant", "subtype", "familial"]):
                    title = candidate
                    break

        try:
            page = wikipedia.page(title, auto_suggest=False)
        except wikipedia.DisambiguationError as e:
            title = e.options[0] if e.options else title
            page = wikipedia.page(title)
        except Exception:
            page = wikipedia.page(title)

        summary = wikipedia.summary(page.title, sentences=3)
        if len(summary) > max_chars:
            summary = summary[:max_chars].rsplit(".", 1)[0] + "..."

        url = getattr(page, "url", f"https://en.wikipedia.org/wiki/{urllib.parse.quote(page.title)}")
        return {"title": page.title, "summary": summary, "url": url}

    except Exception:
        return None

# -----------------------------
# Streamlit app
# -----------------------------
st.set_page_config(page_title="InMind", page_icon="🧠", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Centered logo
st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
st.image("LOGO_PATH.png", width=180)
st.markdown("</div>", unsafe_allow_html=True)

# Disclaimer (centered)
st.markdown(
    "<div style='text-align:center; color:gray; font-size:14px;'>"
    "⚠️ Educational assistant for brain health — not a medical diagnosis tool."
    "</div><br>",
    unsafe_allow_html=True,
)

# Sidebar for FAQs
with st.sidebar:
    st.header("❓ FAQs")
    faq_prompts = {
        "What is dementia?": "Dementia",
        "What causes Alzheimer's?": "Alzheimer's disease",
        "What is Parkinson's disease?": "Parkinson's disease",
        "What is a stroke?": "Stroke",
    }
    for label, query in faq_prompts.items():
        if st.button(label):
            info = query_wikipedia_article(query)
            if info:
                reply = f"**{info['title']}**\n\n{info['summary']}\n\n🔗 [Read more]({info['url']})"
            else:
                reply = "Sorry, I couldn’t find information on that."
            st.session_state.messages.append({"role": "assistant", "content": reply, "time": datetime.now()})
            st.rerun()

    st.divider()
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Show chat history
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# User input
if prompt := st.chat_input("Ask me about brain health... or any topic!"):
    st.session_state.messages.append({"role": "user", "content": prompt, "time": datetime.now()})
    with st.chat_message("user"):
        st.markdown(prompt)

    info = query_wikipedia_article(prompt)
    if info:
        reply = f"I found **{info['title']}** on Wikipedia:\n\n{info['summary']}\n\n🔗 [Read more]({info['url']})"
    else:
        reply = "Sorry, I couldn’t find an answer for that. Please try another term or consult a trusted medical source."

    st.session_state.messages.append({"role": "assistant", "content": reply, "time": datetime.now()})
    with st.chat_message("assistant"):
        st.markdown(reply)
