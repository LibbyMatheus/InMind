import streamlit as st
import wikipedia
import urllib.parse
from datetime import datetime

# -----------------------------
# Emergency detection
# -----------------------------
def detect_emergency(text: str) -> bool:
    emergencies = ["not breathing", "collapsed", "stroke", "seizure", "heart attack"]
    return any(e in text.lower() for e in emergencies)

# -----------------------------
# Health keyword categories
# -----------------------------
HEALTH_KEYWORDS = {
    "memory": ["forgetting", "memory loss", "confusion", "alzheimer", "dementia"],
    "movement": ["shaking", "tremor", "parkinson", "stiffness"],
    "stroke": ["slurred speech", "drooping face", "weakness", "stroke"],
    "vision": ["blurry vision", "double vision", "sight loss"]
}

def detect_health_categories(text: str):
    found = []
    for category, words in HEALTH_KEYWORDS.items():
        for w in words:
            if w in text.lower():
                found.append(category)
                break
    return found

# -----------------------------
# Heuristic advice block
# -----------------------------
def health_advice_block(categories):
    advice = []
    if "memory" in categories:
        advice.append(
            "🧠 Memory issues detected:\n- Could be age-related or linked to conditions like Alzheimer’s.\n"
            "- Next: See a neurologist.\n- Meanwhile: Encourage mental stimulation and daily routines."
        )
    if "movement" in categories:
        advice.append(
            "🤲 Movement issues detected:\n- Possible Parkinson’s or motor-related disorder.\n"
            "- Next: Ask for referral to a movement specialist.\n- Meanwhile: Gentle exercise may help."
        )
    if "stroke" in categories:
        advice.append(
            "⚠️ Stroke signs detected:\n- This is a medical emergency.\n- Call 911 immediately.\n- Do NOT wait."
        )
    if "vision" in categories:
        advice.append(
            "👁️ Vision issues detected:\n- Could be linked to neurological conditions or eye health.\n"
            "- Next: Schedule an ophthalmology exam.\n- Meanwhile: Note sudden changes and seek urgent help if vision is lost."
        )
    return "\n\n".join(advice)

# -----------------------------
# Wikipedia query
# -----------------------------
def query_wikipedia_article(prompt: str, max_chars: int = 900):
    try:
        # Canonical topics
        canonical_topics = {
            "dementia": "Dementia",
            "alzheimer": "Alzheimer's disease",
            "alzheimers": "Alzheimer's disease",
            "stroke": "Stroke (medicine)",
            "parkinson": "Parkinson's disease",
            "memory loss": "Amnesia",
        }

        lower_prompt = prompt.lower()
        for key, page in canonical_topics.items():
            if key in lower_prompt:
                try:
                    page_obj = wikipedia.page(page, auto_suggest=False)
                    summary = wikipedia.summary(page_obj.title, sentences=3)
                    if len(summary) > max_chars:
                        summary = summary[:max_chars].rsplit(".", 1)[0] + "..."
                    return {"title": page_obj.title, "summary": summary, "url": page_obj.url}, [page_obj.title]
                except Exception:
                    pass

        # Normal search
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
            summary = summary[:max_chars].rsplit(".", 1)[0] + "..."

        url = getattr(page, "url", f"https://en.wikipedia.org/wiki/{urllib.parse.quote(page.title)}")
        return {"title": page.title, "summary": summary, "url": url}, results
    except Exception:
        return None, None

# -----------------------------
# Offline fallback
# -----------------------------
def offline_fallback(prompt: str) -> str:
    return "Sorry, I couldn’t find reliable information. Please consult a trusted medical source."

# -----------------------------
# Streamlit app
# -----------------------------
st.set_page_config(page_title="InMind", page_icon="🧠", layout="centered")

# Dark background
st.markdown(
    """
    <style>
    .stApp {background-color: #000000; color: #FFFFFF;}
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.last_wiki = None
    st.session_state.query_count = 0
    st.session_state.favorites = []

# Logo (centered)
st.image("LOGO_PATH.png", use_container_width=False, width=250)

# Disclaimer (left-aligned)
st.markdown(
    "Educational assistant for brain health — not a medical diagnosis tool.",
    unsafe_allow_html=True
)

# -----------------------------
# Sidebar FAQs
# -----------------------------
with st.sidebar:
    st.header("⚙️ Settings & Tools")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.query_count = 0
        st.session_state.last_wiki = None
        st.session_state.favorites = []

    st.subheader("⭐ Favorites")
    if st.session_state.favorites:
        for f in st.session_state.favorites:
            st.markdown(f"- {f[:80]}...")
    else:
        st.caption("No favorites saved yet.")

    if st.button("⬇️ Download Chat (TXT)"):
        transcript = ""
        for m in st.session_state.messages:
            transcript += f"[{m['time'].strftime('%H:%M')}] {m['role'].title()}: {m['content']}\n\n"
        st.download_button("Save File", transcript, "chat.txt")

    st.subheader("❓ FAQs")
    faq_prompts = {
        "What is dementia?": "Dementia",
        "What causes Alzheimer's?": "Alzheimer's disease",
        "What is Parkinson's disease?": "Parkinson's disease",
        "What is ALS?": "Amyotrophic lateral sclerosis"
    }

    for label, query in faq_prompts.items():
        if st.button(label):
            info, _ = query_wikipedia_article(query)
            if info:
                reply = (
                    f"**{info['title']}**\n\n{info['summary']}\n\n"
                    f"Read more: {info['url']}\n\n"
                    "What to do next:\n"
                    "- Consult a healthcare professional for guidance.\n"
                    "- Visit the resources page for caregiving tips, brain exercises, and questions to ask your doctor."
                )
                st.session_state.messages.append({"role": "assistant", "content": reply, "time": datetime.now()})

# -----------------------------
# Show chat history
# -----------------------------
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# -----------------------------
# Handle new user input
# -----------------------------
if prompt := st.chat_input("Ask me about brain health..."):
    st.session_state.messages.append({"role": "user", "content": prompt, "time": datetime.now()})
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.query_count += 1

    # Emergency check
    if detect_emergency(prompt):
        reply = "🚨 Emergency detected. Please call 911 immediately. Do not wait."
        st.session_state.messages.append({"role": "assistant", "content": reply, "time": datetime.now()})
        with st.chat_message("assistant"):
            st.markdown(reply)
    else:
        info, results = query_wikipedia_article(prompt)
        if info:
            reply = (
                f"I found **{info['title']}** on Wikipedia:\n\n{info['summary']}\n\nRead more: {info['url']}\n\n"
                "What to do next:\n- Consult a healthcare professional for guidance.\n"
                "- Visit the resources page for caregiving tips, brain exercises, and questions to ask your doctor."
            )
            st.session_state.last_wiki = info['title']
            st.session_state.messages.append({"role": "assistant", "content": reply, "time": datetime.now()})
            with st.chat_message("assistant"):
                st.markdown(reply)
            if st.button("⭐ Save last answer"):
                st.session_state.favorites.append(reply)
        else:
            categories = detect_health_categories(prompt)
            if categories:
                advice_text = health_advice_block(categories)
                advice_text += "\n\n*This is a heuristic suggestion, not a diagnosis.*"
                st.session_state.messages.append({"role": "assistant", "content": advice_text, "time": datetime.now()})
                with st.chat_message("assistant"):
                    st.markdown(advice_text)
            else:
                reply = offline_fallback(prompt)
                st.session_state.messages.append({"role": "assistant", "content": reply, "time": datetime.now()
