# app.py
import streamlit as st
import wikipedia
import re
import urllib.parse
from datetime import datetime

# -------------------------------
# Page config & styling (KEEP)
# -------------------------------
st.set_page_config(page_title="InMind", layout="wide")
ACCENT = "#FDD2DC"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: #000000;
        color: #ffffff;
    }}
    h1, h2, h3 {{
        color: #ffffff;
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
    }}
    a, .accent {{ color: {ACCENT}; }}
    .stChatMessage {{
        font-size: 1.05em;
        line-height: 1.6;
        padding: 0.6em 1em;
        border-radius: 8px;
        margin-bottom: 0.5em;
    }}
    .footer {{
        font-size: 0.8em;
        text-align: center;
        color: #888888;
        margin-top: 3em;
    }}
    div[data-baseweb="base-input"] > div {{
        border-color: {ACCENT} !important;
    }}
    button[kind="primary"] {{
        background: {ACCENT} !important;
        color: #000 !important;
        border-radius: 8px !important;
    }}
    [data-testid="stImage"] {{
        display: flex;
        justify-content: center;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------
# Branding: logo centered (KEEP)
# -------------------------------
LOGO_FILENAME = "LOGO_PATH.png"
GITHUB_RAW = f"https://raw.githubusercontent.com/libbymatheus/InMind/main/{LOGO_FILENAME}"

st.markdown(
    f"""
    <div style="display:flex; justify-content:center; align-items:center; margin-bottom:12px;">
        <img src="{GITHUB_RAW}" alt="InMind Logo" width="200" style="display:block;"/>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="text-align: center; font-size:18px;">
        A free, conversational assistant powered by Wikipedia.
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------------
# Session state & defaults
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi — I'm InMind. I specialize in brain health and general information. Ask me anything!",
            "time": datetime.now(),
        }
    ]
if "query_count" not in st.session_state:
    st.session_state.query_count = 0
if "last_wiki" not in st.session_state:
    st.session_state.last_wiki = None
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "lang" not in st.session_state:
    st.session_state.lang = "en"

MAX_QUERIES = 30

# -------------------------------
# Sidebar: language, usage, FAQs, favorites, resources
# -------------------------------
with st.sidebar:
    st.header("Session")
    st.write(f"Queries used: **{st.session_state.query_count} / {MAX_QUERIES}**")

    st.markdown("---")
    st.header("Language")
    lang_choice = st.selectbox("Choose language", options=["English", "Spanish", "French"], index=["English","Spanish","French"].index(
        "English" if st.session_state.lang == "en" else ("Spanish" if st.session_state.lang == "es" else "French")
    ))
    lang_map = {"English": "en", "Spanish": "es", "French": "fr"}
    chosen_code = lang_map[lang_choice]
    if chosen_code != st.session_state.lang:
        st.session_state.lang = chosen_code
        wikipedia.set_lang(st.session_state.lang)

    st.markdown("---")
    st.header("Quick FAQs")
    faq_questions = [
        "What is Alzheimer's disease?",
        "What causes dementia?",
        "How to support someone with memory problems?",
        "What are common stroke warning signs?",
        "How to improve sleep hygiene?"
    ]
    for q in faq_questions:
        if st.button(q, key=f"faq_{q}"):
            st.session_state.messages.append({"role":"user","content":q,"time":datetime.now()})
            st.rerun()

    st.markdown("---")
    st.header("Favorites")
    if st.session_state.favorites:
        for i, fav in enumerate(st.session_state.favorites[::-1]):
            st.markdown(f"**{fav['title']}** — {fav['time'].strftime('%Y-%m-%d %H:%M')}")
            st.write(fav["content"])
            if st.button(f"Remove ⭐ {i}", key=f"remfav_{i}"):
                to_remove = st.session_state.favorites[::-1][i]
                st.session_state.favorites = [f for f in st.session_state.favorites if not (f["title"]==to_remove["title"] and f["time"]==to_remove["time"])]
                st.rerun()
    else:
        st.write("No favorites yet. Save answers you find helpful with the ⭐ button.")

    st.markdown("---")
    st.header("Trusted resources")
    st.markdown("- [Mayo Clinic](https://www.mayoclinic.org/)")
    st.markdown("- [NIH](https://www.nih.gov/)")
    st.markdown("- [MedlinePlus](https://medlineplus.gov/)")
    st.markdown("- [WHO](https://www.who.int/)")

# Ensure wikipedia language set
wikipedia.set_lang(st.session_state.lang)

# -------------------------------
# Utilities: (same as before)
# -------------------------------
def is_follow_up(text: str) -> bool:
    text = text.strip().lower()
    if len(text.split()) <= 4:
        return True
    if re.search(r'\b(it|they|them|he|she|that|those|this|these)\b', text):
        return True
    if re.match(r'^(and|also|what about|how about|then|more)\b', text):
        return True
    return False

def query_wikipedia_article(prompt: str, max_chars: int = 900):
    try:
        results = wikipedia.search(prompt, results=3)
        if not results:
            return None, None
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
            summary = summary[:max_chars].rsplit(".",1)[0] + "..."
        url = getattr(page, "url", f"https://{st.session_state.lang}.wikipedia.org/wiki/{urllib.parse.quote(page.title)}")
        return {"title": page.title, "summary": summary, "url": url}, results
    except Exception:
        return None, None

def extract_relevant_sentences(page_title: str, terms: list, max_sentences: int = 3):
    try:
        page = wikipedia.page(page_title)
        content = page.content
        sentences = re.split(r'(?<=[.!?])\s+', content)
        matches = []
        qterms = [q.lower() for q in terms if q]
        for s in sentences:
            sl = s.lower()
            if any(q in sl for q in qterms):
                matches.append(s.strip())
                if len(matches) >= max_sentences:
                    break
        if matches:
            return " ".join(matches)
        return wikipedia.summary(page.title, sentences=max_sentences)
    except Exception:
        return None

# -------------------------------
# Offline fallback message
# -------------------------------
def offline_fallback(user_query):
    tip = (
        "I couldn't reach Wikipedia or find a clear article. "
        "If this is a health concern, consider contacting a clinician. "
        "Quick resources: Mayo Clinic, NIH, MedlinePlus (links in sidebar)."
    )
    return tip

# -------------------------------
# Render existing history
# -------------------------------
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# -------------------------------
# Main chat input logic
# -------------------------------
if st.session_state.query_count >= MAX_QUERIES:
    st.warning("You have reached the session limit. Clear Chat to start a new session.")
else:
    if prompt := st.chat_input("Type your question here..."):
        st.session_state.query_count += 1
        st.session_state.messages.append({"role":"user","content":prompt,"time":datetime.now()})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Emergency check
        if re.search(r'\b(call 911|911|emergency|unresponsive|not breathing|sudden vision|face droop|arm weak|loss of speech|collapse)\b', prompt.lower()):
            em = "If this is an emergency (sudden weakness, face droop, loss of speech, unresponsiveness), call emergency services immediately. This tool is not for emergencies."
            st.session_state.messages.append({"role":"assistant","content":em,"time":datetime.now()})
            with st.chat_message("assistant"):
                st.markdown(em)
            st.session_state.last_wiki = None
        else:
            # Wikipedia lookup
            info, results = query_wikipedia_article(prompt)
            if info:
                reply = f"I found **{info['title']}** on Wikipedia:\n\n{info['summary']}\n\nRead more: {info['url']}"
                st.session_state.last_wiki = info['title']
            else:
                reply = offline_fallback(prompt)
            st.session_state.messages.append({"role":"assistant","content":reply,"time":datetime.now()})
            with st.chat_message("assistant"):
                st.markdown(reply)

# -------------------------------
# Actions: Clear Chat + Favorites + Download transcript
# -------------------------------
st.markdown("---")
col1, col2, col3 = st.columns([1,1,1])

with col1:
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = [
            {
                "role":"assistant",
                "content":"Hi — I'm InMind. I specialize in brain health and general info. Ask me anything!",
                "time":datetime.now()
            }
        ]
        st.session_state.query_count = 0
        st.session_state.last_wiki = None
        st.rerun()

with col2:
    last_assistant = None
    for m in reversed(st.session_state.messages):
        if m["role"] == "assistant":
            last_assistant = m
            break
    if last_assistant:
        if st.button("⭐ Save last answer"):
            fav = {
                "title": (last_assistant.get("meta", {}).get("title") or last_assistant["content"][:40]+"..."),
                "content": last_assistant["content"],
                "url": last_assistant.get("meta", {}).get("url"),
                "time": datetime.now()
            }
            st.session_state.favorites.append(fav)
            st.success("Saved to Favorites")

with col3:
    if st.session_state.messages:
        transcript = "InMind Chat Transcript\n"
        transcript += f"Session started: {st.session_state.messages[0]['time'].strftime('%Y-%m-%d %H:%M:%S')}\n"
        transcript += "-"*40 + "\n\n"
        for m in st.session_state.messages:
            ts = m["time"].strftime("%H:%M:%S")
            speaker = "You" if m["role"]=="user" else "InMind"
            meta = m.get("meta", {})
            line = f"[{ts}] {speaker}: {m['content']}"
            if meta.get("url"):
                line += f" (source: {meta['url']})"
            transcript += line + "\n\n"
        st.download_button("⬇️ Download Chat (TXT)", data=transcript, file_name="inmind_chat.txt", mime="text/plain")

# -------------------------------
# Footer / Disclaimer (KEEP)
# -------------------------------
st.markdown(
    "<div class='footer'>Disclaimer: InMind is for educational purposes only and does not provide medical diagnoses. Always consult a licensed healthcare professional for medical advice.</div>",
    unsafe_allow_html=True,
)
