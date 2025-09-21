import streamlit as st
import wikipedia
import urllib.parse
from langdetect import detect
from deep_translator import GoogleTranslator

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
if "query_count" not in st.session_state:
    st.session_state.query_count = 0
if "last_wiki" not in st.session_state:
    st.session_state.last_wiki = None
if "lang" not in st.session_state:
    st.session_state.lang = "en"

# ---------------------------
# Language Selector
# ---------------------------
lang_names = {
    "en": "English",
    "es": "Español",
    "pt": "Português",
    "fr": "Français"
}
st.sidebar.title("🌐 Language")
lang_choice = st.sidebar.radio("Choose language:", list(lang_names.keys()), format_func=lambda x: lang_names[x])
st.session_state.lang = lang_choice
wikipedia.set_lang("en")  # always use English Wikipedia for consistency

# ---------------------------
# FAQ translations
# ---------------------------
faq_translations = {
    "en": [
        ("What causes dementia?", "dementia"),
        ("What are the early signs of Alzheimer’s?", "alzheimer"),
        ("How can stroke affect memory?", "stroke"),
        ("What are the symptoms of Parkinson’s?", "parkinson"),
    ],
    "es": [
        ("¿Qué causa la demencia?", "dementia"),
        ("¿Cuáles son los primeros signos del Alzheimer?", "alzheimer"),
        ("¿Cómo puede un derrame cerebral afectar la memoria?", "stroke"),
        ("¿Cuáles son los síntomas del Parkinson?", "parkinson"),
    ],
    "pt": [
        ("O que causa a demência?", "dementia"),
        ("Quais são os primeiros sinais do Alzheimer?", "alzheimer"),
        ("Como o AVC pode afetar a memória?", "stroke"),
        ("Quais são os sintomas do Parkinson?", "parkinson"),
    ],
    "fr": [
        ("Quelles sont les causes de la démence ?", "dementia"),
        ("Quels sont les premiers signes de la maladie d’Alzheimer ?", "alzheimer"),
        ("Comment un AVC peut-il affecter la mémoire ?", "stroke"),
        ("Quels sont les symptômes de la maladie de Parkinson ?", "parkinson"),
    ]
}

# ---------------------------
# Caching Helpers
# ---------------------------
@st.cache_data(show_spinner=False)
def cached_translate(text, target_lang):
    """Translate text and cache results to save API calls."""
    if target_lang == "en":
        return text
    try:
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
    except Exception:
        return text

@st.cache_data(show_spinner=False)
def cached_wikipedia_query(prompt: str, topic_key: str = None, max_chars: int = 900):
    """Query Wikipedia and cache results for repeated queries."""
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
                return None, None
            title = results[0]
            if any(word in title.lower() for word in ["childhood", "variant", "subtype", "familial"]):
                for candidate in results[1:]:
                    if not any(w in candidate.lower() for w in ["childhood", "variant", "subtype", "familial"]):
                        title = candidate
                        break
            try:
                page_obj = wikipedia.page(title, auto_suggest=False)
            except wikipedia.DisambiguationError as e:
                title = e.options[0] if e.options else title
                page_obj = wikipedia.page(title)
            summary = wikipedia.summary(page_obj.title, sentences=3)

        if len(summary) > max_chars:
            summary = summary[:max_chars].rsplit(".", 1)[0] + "..."

        return {
            "title": page_obj.title,
            "summary": summary,
            "url": page_obj.url
        }, [page_obj.title]

    except Exception:
        return None, None

# ---------------------------
# Header with Logo
# ---------------------------
st.image("https://i.imgur.com/6Iej2cO.png", width=120)
st.title("🧠 InMind")
st.write({
    "en": "Your companion for brain health resources.",
    "es": "Tu compañero para recursos sobre la salud cerebral.",
    "pt": "Seu companheiro para recursos sobre saúde cerebral.",
    "fr": "Votre compagnon pour les ressources sur la santé du cerveau."
}[st.session_state.lang])

# ---------------------------
# FAQ Section
# ---------------------------
st.subheader({
    "en": "Common Questions",
    "es": "Preguntas comunes",
    "pt": "Perguntas comuns",
    "fr": "Questions fréquentes"
}[st.session_state.lang])

faq_col1, faq_col2 = st.columns(2)
for i, (label, topic_key) in enumerate(faq_translations[st.session_state.lang]):
    if i % 2 == 0:
        if faq_col1.button(label):
            wiki, _ = cached_wikipedia_query(label, topic_key=topic_key)
            if wiki:
                translated_summary = cached_translate(wiki["summary"], st.session_state.lang)
                st.session_state.messages.append(("assistant", translated_summary))
                st.session_state.last_wiki = wiki
    else:
        if faq_col2.button(label):
            wiki, _ = cached_wikipedia_query(label, topic_key=topic_key)
            if wiki:
                translated_summary = cached_translate(wiki["summary"], st.session_state.lang)
                st.session_state.messages.append(("assistant", translated_summary))
                st.session_state.last_wiki = wiki

# ---------------------------
# Chat Input
# ---------------------------
user_input = st.chat_input({
    "en": "Ask about brain health...",
    "es": "Pregunta sobre la salud cerebral...",
    "pt": "Pergunte sobre a saúde cerebral...",
    "fr": "Posez une question sur la santé du cerveau..."
}[st.session_state.lang])

if user_input:
    st.session_state.messages.append(("user", user_input))

    # Detect & translate user query into English for Wikipedia
    try:
        detected_lang = detect(user_input)
    except Exception:
        detected_lang = "en"
    translated_prompt = GoogleTranslator(source="auto", target="en").translate(user_input)

    wiki, _ = cached_wikipedia_query(translated_prompt)
    if wiki:
        translated_summary = cached_translate(wiki["summary"], st.session_state.lang)
        st.session_state.messages.append(("assistant", translated_summary))
        st.session_state.last_wiki = wiki
    else:
        st.session_state.messages.append(("assistant", {
            "en": "Sorry, I couldn’t find information on that.",
            "es": "Lo siento, no pude encontrar información sobre eso.",
            "pt": "Desculpe, não consegui encontrar informações sobre isso.",
            "fr": "Désolé, je n’ai pas trouvé d’informations à ce sujet."
        }[st.session_state.lang]))

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
    st.session_state.query_count = 0
    st.session_state.last_wiki = None
    st.session_state.favorites = []
    st.rerun()

# ---------------------------
# Favorites Display
# ---------------------------
if st.session_state.favorites:
    st.subheader({
        "en": "⭐ Favorites",
        "es": "⭐ Favoritos",
        "pt": "⭐ Favoritos",
        "fr": "⭐ Favoris"
    }[st.session_state.lang])
    for fav in st.session_state.favorites:
        translated_summary = cached_translate(fav["summary"], st.session_state.lang)
        st.markdown(f"**[{fav['title']}]({fav['url']})** - {translated_summary}")
