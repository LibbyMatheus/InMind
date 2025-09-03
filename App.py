import streamlit as st
from openai import OpenAI
import os

# -------------------------------
# Setup OpenAI API
# -------------------------------
# IMPORTANT: You’ll need to set your OpenAI API key in Streamlit Cloud
# Go to Settings > Secrets and add: OPENAI_API_KEY="your_api_key_here"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# -------------------------------
# Page Setup
# -------------------------------
st.set_page_config(page_title="InMind AI", layout="centered")

# Custom Styling
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
    .stChatMessage {{
        font-size: 1.05em;
        line-height: 1.6;
    }}
    .accent {{
        color: #FDD2DC;
        font-weight: bold;
    }}
    .footer {{
        font-size: 0.8em;
        text-align: center;
        color: #888888;
        margin-top: 3em;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# Branding
# -------------------------------
st.image("40AC5C5C-6240-4E68-A3BB-4FEC1401B99C.jpeg", width=200)
st.title("🧠 InMind AI")
st.write("Your conversational assistant, specializing in **health and neuroscience**. Not a diagnostic tool.")

# -------------------------------
# Session State
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm InMind. Ask me anything — I specialize in health but can chat about anything."}
    ]

# -------------------------------
# Display Chat History
# -------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------------
# User Input
# -------------------------------
if prompt := st.chat_input("Type your question here..."):
    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # -------------------------------
    # OpenAI API Call
    # -------------------------------
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Lightweight and fast model
            messages=[
                {"role": "system", "content": (
                    "You are InMind, a supportive, trustworthy AI assistant. "
                    "You can answer general questions, but you are especially good at health, brain health, "
                    "and neurodegenerative disease awareness. "
                    "For health questions, provide structured answers: possible causes, next steps, and what to do meanwhile. "
                    "Always include a disclaimer: 'This is not medical advice. Please consult a doctor.'"
                )},
                *st.session_state.messages
            ],
            max_tokens=400,
            temperature=0.7
        )

        reply = response.choices[0].message.content.strip()

    except Exception as e:
        reply = f"⚠️ Error: {e}"

    # -------------------------------
    # Show Assistant Reply
    # -------------------------------
    with st.chat_message("assistant"):
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

# -------------------------------
# Disclaimer
# -------------------------------
st.markdown("---")
st.markdown(
    "<div class='footer'>Disclaimer: InMind AI is for educational purposes only and does not provide medical diagnoses. Always consult a healthcare professional for medical advice.</div>",
    unsafe_allow_html=True
)
