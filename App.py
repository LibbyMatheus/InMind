import streamlit as st
from openai import OpenAI
import os

# -------------------------------
# Config & Styling
# -------------------------------
st.set_page_config(page_title="InMind", layout="centered")

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
    .stChatMessage {{ font-size: 1.05em; line-height: 1.6; }}
    .footer {{ font-size: 0.8em; text-align: center; color: #888888; margin-top: 3em; }}
    /* Tweak text input border to accent */
    div[data-baseweb="base-input"] > div {{
        border-color: {ACCENT} !important;
    }}
    button[kind="primary"] {{
        background: {ACCENT} !important;
        color: #000 !important;
        border-radius: 8px !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# Branding (upload your logo to the repo root)
# Make sure the filename matches exactly:
#   40AC5C5C-6240-4E68-A3BB-4FEC1401B99C.jpeg
# Or rename it to 'logo.png' and change the line below.
# -------------------------------
LOGO_PATH = "40AC5C5C-6240-4E68-A3BB-4FEC1401B99C.jpeg"
try:
    st.image(LOGO_PATH, width=200)
except Exception:
    st.write(f"*Logo file not found: `{LOGO_PATH}`. Upload it to your repo or update `LOGO_PATH`.*")

st.title("🧠 InMind AI")
st.write("A conversational assistant that can chat about anything, with a focus on **health and neuroscience**. This is **not** a diagnostic tool.")

# -------------------------------
# OpenAI client (with clear error if key missing)
# -------------------------------
api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
if not api_key:
    st.error("Missing OpenAI API key. In Streamlit Cloud, go to Settings → Secrets and set OPENAI_API_KEY.")
    st.stop()

client = OpenAI(api_key=api_key)

# -------------------------------
# Conversation state
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": (
            "You are InMind, a supportive, trustworthy AI assistant. "
            "You can answer general questions on any topic, but you are especially strong at health, "
            "brain health, and neurodegenerative disease awareness. "
            "For health questions, provide structured answers: possible causes (not diagnoses), "
            "red flags, next steps (who to see, what tests to ask about), and what to do meanwhile. "
            "Be clear, kind, and practical. Avoid definitive diagnoses. "
            "Always include: 'This is not medical advice. Please consult a clinician.'"
        )},
        {"role": "assistant", "content": "Hi! I’m InMind. Ask me anything — I specialize in health but can chat about anything."}
    ]

# Show history
for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------------
# Chat input → OpenAI
# -------------------------------
prompt = st.chat_input("Type your question here...")
if prompt:
    # Show + store user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call OpenAI
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",      # fast, capable model; change if you prefer
            messages=st.session_state.messages,
            temperature=0.7,
            max_tokens=600,
        )
        reply = resp.choices[0].message.content.strip()
    except Exception as e:
        reply = f"⚠️ Could not generate a reply: {e}"

    # Show + store assistant reply
    with st.chat_message("assistant"):
        st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})

# -------------------------------
# Disclaimer
# -------------------------------
st.markdown("---")
st.markdown(
    "<div class='footer'>Disclaimer: InMind AI is for educational purposes only and does not provide medical diagnoses. Always consult a licensed healthcare professional for medical advice.</div>",
    unsafe_allow_html=True
)
