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
    st.session_state.favorites = []  # list of dicts {title, content, url, time}
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
    # map back to code
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
            # simulate user asking
            st.session_state.messages.append({"role":"user","content":q,"time":datetime.now()})
            st.experimental_rerun()

    st.markdown("---")
    st.header("Favorites")
    if st.session_state.favorites:
        for i, fav in enumerate(st.session_state.favorites[::-1]):  # newest first
            st.markdown(f"**{fav['title']}** — {fav['time'].strftime('%Y-%m-%d %H:%M')}")
            st.write(fav["content"])
            if st.button(f"Remove ⭐ {i}", key=f"remfav_{i}"):
                # remove by matching time/title (simple)
                to_remove = st.session_state.favorites[::-1][i]
                st.session_state.favorites = [f for f in st.session_state.favorites if not (f["title"]==to_remove["title"] and f["time"]==to_remove["time"])]
                st.experimental_rerun()
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
# Utilities: heuristics, wiki lookup, fallback
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
            # choose the first reasonable option
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

HEALTH_KEYWORDS = {
    "memory": ["memory", "forget", "dementia", "alzheimer", "confusion", "repeating"],
    "movement": ["tremor", "shake", "parkinson", "stiff", "rigid", "bradykinesia", "slow movement"],
    "stroke": ["stroke", "face droop", "arm weak", "slurred", "speech difficulty", "sudden weakness"],
    "speech": ["speech", "aphasia", "language", "word-finding", "slurred"],
    "sleep": ["sleep", "insomnia", "apnea", "narcolepsy", "restless legs", "daytime sleepiness"],
    "mood": ["depress", "anxiety", "panic", "stress", "hopeless", "sad"],
    "seizure": ["seizure", "convulsion", "fit", "blackout", "epilepsy"],
    "headache": ["headache", "migraine", "aura", "thunderclap"],
    "vision": ["vision", "double vision", "blur", "blind"],
    "numbness": ["numb", "tingle", "pins and needles", "neuropathy"],
}

def detect_health_categories(text: str):
    t = text.lower()
    found = []
    for cat, kws in HEALTH_KEYWORDS.items():
        for kw in kws:
            if kw in t:
                found.append(cat)
                break
    return found

def health_advice_block(categories):
    out_parts = []
    advice_map = {
        "memory": (
            "Possible area: Alzheimer’s-type cognitive decline.",
            "Watch: progressive short-term memory loss, repeating questions, disorientation.",
            "Next steps: schedule cognitive screen (MMSE/MoCA), bring family member, keep diary.",
            "Meanwhile: support sleep, exercise, cognitive tasks, safety measures."
        ),
        "movement": (
            "Possible area: Movement disorder (e.g., Parkinson’s).",
            "Watch: tremor, slowed movements, small handwriting, balance problems.",
            "Next steps: movement-neurology evaluation; record short videos of symptoms.",
            "Meanwhile: fall safety, gentle exercise; do not stop meds."
        ),
        "stroke": (
            "Possible area: Stroke (urgent if sudden).",
            "Watch: FAST — Face droop, Arm weakness, Speech difficulty; sudden onset is emergency.",
            "Next steps: call emergency services immediately for sudden symptoms.",
            "Meanwhile: note time of onset; do not drive."
        ),
        "speech": (
            "Possible area: Language disorder (aphasia/PPA).",
            "Watch: difficulty finding words, understanding, forming sentences.",
            "Next steps: speech-language evaluation and neurology assessment.",
            "Meanwhile: use communication aids and consistency."
        ),
        "sleep": (
            "Possible area: Sleep disorder (insomnia, sleep apnea, RLS).",
            "Watch: loud snoring, gasping, daytime sleepiness.",
            "Next steps: keep sleep diary; consult primary care / sleep clinic.",
            "Meanwhile: regular schedule, cut caffeine/alcohol before bed."
        ),
        "mood": (
            "Possible area: Mood disorder (depression/anxiety).",
            "Watch: prolonged low mood, panic, changes in sleep/appetite.",
            "Next steps: mental health screening; consider therapy or medication discussion.",
            "Meanwhile: reach out to supports; if suicidal, seek emergency help."
        ),
        "seizure": (
            "Possible area: Seizure disorder.",
            "Watch: convulsions, loss of awareness, tongue biting, post-event confusion.",
            "Next steps: urgent neurology and EEG for first-time events; ED if prolonged.",
            "Meanwhile: safety and avoid driving until assessed."
        ),
        "headache": (
            "Possible area: Headache / migraine.",
            "Watch: sudden severe headache (thunderclap), focal deficits.",
            "Next steps: ED for sudden severe; otherwise track triggers and consult clinician.",
            "Meanwhile: hydration, rest, avoid triggers."
        ),
        "vision": (
            "Possible area: Visual disturbance.",
            "Watch: sudden loss/double vision.",
            "Next steps: urgent ophthalmology/ED if sudden.",
            "Meanwhile: avoid driving if impaired."
        ),
        "numbness": (
            "Possible area: Peripheral neuropathy.",
            "Watch: progressive numbness, burning, weakness.",
            "Next steps: primary-care testing (glucose, B12) and neurology referral.",
            "Meanwhile: protective foot care and fall prevention."
        ),
    }
    for c in categories:
        if c in advice_map:
            adv = advice_map[c]
            out_parts.append(f"**{adv[0]}**\n\n{adv[1]}\n\n**Next steps:** {adv[2]}\n\n{adv[3]}")
    return "\n\n---\n\n".join(out_parts)

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
        # store user message
        st.session_state.messages.append({"role":"user","content":prompt,"time":datetime.now()})
        with st.chat_message("user"):
            st.markdown(prompt)

        # emergency pattern check
        if re.search(r'\b(call 911|911|emergency|unresponsive|not breathing|sudden vision|face droop|arm weak|loss of speech|collapse)\b', prompt.lower()):
            em = "If this is an emergency (sudden weakness, face droop, loss of speech, unresponsiveness), call emergency services immediately. This tool is not for emergencies."
            st.session_state.messages.append({"role":"assistant","content":em,"time":datetime.now()})
            with st.chat_message("assistant"):
                st.markdown(em)
            st.session_state.last_wiki = None
        else:
            # health-first detection
            categories = detect_health_categories(prompt)
            if categories:
                advice_text = health_advice_block(categories)
                advice_text += "\n\n*This is a heuristic suggestion, not a diagnosis.*"
                st.session_state.messages.append({"role":"assistant","content":advice_text,"time":datetime.now()})
                with st.chat_message("assistant"):
                    st.markdown(advice_text)
                st.session_state.last_wiki = None
            else:
                # try Wikipedia
                try:
                    # follow-up handling
                    if is_follow_up(prompt) and st.session_state.last_wiki:
                        extract = extract_relevant_sentences(st.session_state.last_wiki, [prompt], max_sentences=3)
                        if extract:
                            reply = f"I used context from **{st.session_state.last_wiki}**:\n\n{extract}\n\n(Full article: https://{st.session_state.lang}.wikipedia.org/wiki/{urllib.parse.quote(st.session_state.last_wiki)})"
                            st.session_state.messages.append({"role":"assistant","content":reply,"time":datetime.now(),"meta":{"url":f"https://{st.session_state.lang}.wikipedia.org/wiki/{urllib.parse.quote(st.session_state.last_wiki)}"}})
                            with st.chat_message("assistant"):
                                st.markdown(reply)
                        else:
                            info, results = query_wikipedia_article(prompt)
                            if info:
                                reply = f"I found **{info['title']}** on Wikipedia:\n\n{info['summary']}\n\nRead more: {info['url']}"
                                st.session_state.last_wiki = info['title']
                            else:
                                reply = offline_fallback(prompt)
                            st.session_state.messages.append({"role":"assistant","content":reply,"time":datetime.now()})
                            with st.chat_message("assistant"):
                                st.markdown(reply)
                    else:
                        info, results = query_wikipedia_article(prompt)
                        if info:
                            reply = f"I found **{info['title']}** on Wikipedia:\n\n{info['summary']}\n\nRead more: {info['url']}"
                            st.session_state.last_wiki = info['title']
                            st.session_state.messages.append({"role":"assistant","content":reply,"time":datetime.now(),"meta":{"url":info["url"]}})
                            with st.chat_message("assistant"):
                                st.markdown(reply)
                            # suggested follow-ups (richer)
                            suggestions = [
                                f"What are the causes of {info['title']}?",
                                f"What are common symptoms of {info['title']}?",
                                f"What are treatment options for {info['title']}?",
                                f"How can {info['title']} be prevented?",
                                f"What is the prognosis for {info['title']}?"
                            ]
                            cols = st.columns(len(suggestions))
                            for i, s in enumerate(suggestions):
                                if cols[i].button(s, key=f"sf_{st.session_state.query_count}_{i}"):
                                    # append simulated user query and run quick path
                                    st.session_state.messages.append({"role":"user","content":s,"time":datetime.now()})
                                    with st.chat_message("user"):
                                        st.markdown(s)
                                    info2, _ = query_wikipedia_article(s)
                                    if info2:
                                        reply2 = f"I found **{info2['title']}**:\n\n{info2['summary']}\n\nRead more: {info2['url']}"
                                    else:
                                        reply2 = "I couldn't find more on that topic."
                                    st.session_state.messages.append({"role":"assistant","content":reply2,"time":datetime.now()})
                                    with st.chat_message("assistant"):
                                        st.markdown(reply2)
                                    st.experimental_rerun()
                        else:
                            # offline fallback
                            reply = offline_fallback(prompt)
                            st.session_state.messages.append({"role":"assistant","content":reply,"time":datetime.now()})
                            with st.chat_message("assistant"):
                                st.markdown(reply)
                except Exception:
                    # safe fallback
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
        st.experimental_rerun()

with col2:
    # Save last assistant reply as favorite (if present)
    last_assistant = None
    for m in reversed(st.session_state.messages):
        if m["role"] == "assistant":
            last_assistant = m
            break
    if last_assistant:
        if st.button("⭐ Save last answer"):
            # build favorite item
            fav = {
                "title": (last_assistant.get("meta", {}).get("title") or last_assistant["content"][:40]+"..."),
                "content": last_assistant["content"],
                "url": last_assistant.get("meta", {}).get("url"),
                "time": datetime.now()
            }
            st.session_state.favorites.append(fav)
            st.success("Saved to Favorites")

with col3:
    # download transcript
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
