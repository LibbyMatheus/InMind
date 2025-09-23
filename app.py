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
# Symptom-to-condition mapping
# -----------------------------
SYMPTOM_MAP = {
    "memory loss": "Dementia",
    "forgetting": "Dementia",
    "confusion": "Delirium",
    "slurred speech": "Stroke",
    "drooping face": "Stroke",
    "weakness": "Stroke",
    "tremor": "Parkinson's disease",
    "shaking": "Parkinson's disease",
    "stiffness": "Parkinson's disease",
    "blurry vision": "Multiple sclerosis",
    "double vision": "Multiple sclerosis",
    "seizure": "Epilepsy"
}

# -----------------------------
# Wikipedia query with causes
# -----------------------------
def query_wikipedia_article(prompt: str, max_chars: int = 900):
    try:
        lower_prompt = prompt.lower()

        # ✅ Symptom matching first
        for symptom, condition in SYMPTOM_MAP.items():
            if symptom in lower_prompt:
                try:
                    page_obj = wikipedia.page(condition, auto_suggest=False)
                    summary = wikipedia.summary(page_obj.title, sentences=3)
                    return {
                        "title": page_obj.title,
                        "summary": f"Based on your symptoms, this may relate to **{page_obj.title}**.\n\n{summary}",
                        "url": page_obj.url
                    }
                except Exception:
                    pass

        # ✅ Canonical topic preference
        for key, page in CANONICAL_TOPICS.items():
            if key in lower_prompt:
                try:
                    page_obj = wikipedia.page(page, auto_suggest=False)
                    summary = wikipedia.summary(page_obj.title, sentences=3)

                    # Look for causes section if asked
                    if any(w in lower_prompt for w in ["cause", "risk factor", "reason"]):
                        try:
                            content = page_obj.content
                            for section in ["Cause", "Causes", "Risk factors", "Etiology"]:
                                if section.lower() in content.lower():
                                    snippet = content.split(section, 1)[1][:max_chars]
                                    return {
                                        "title": page_obj.title,
                                        "summary": f"Here’s what Wikipedia lists under **{section}**:\n\n{snippet}...",
                                        "url": page_obj.url
                                    }
                        except Exception:
                            pass

                    return {
                        "title": page_obj.title,
                        "summary": summary,
                        "url": page_obj.url
                    }
                except Exception:
                    pass

        # ✅ Normal Wikipedia search (prefer exact term first)
        results = wikipedia.search(prompt, results=5)
        if not results:
            return None

        title = results[0]
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

# Centered logo + title
st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
st.image("LOGO_PATH.png", width=180)
st.markdown("<h2 style='text-align:center;'>🧠 InMind — Brain Health Assistant</h2>", unsafe_allow_html=True)
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
        "What causes Alzheimer's?": "Causes of Alzheimer's disease",
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
if prompt := st.chat_input("Describe symptoms or ask any brain health question..."):
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
