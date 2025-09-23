import streamlit as st
import wikipedia
from pathlib import Path

# ------------------------
# Page Config
# ------------------------
st.set_page_config(page_title="InMind", layout="wide")

# ------------------------
# Centered Logo
# ------------------------
LOGO_FILE = Path("LOGO_PATH.png")
if LOGO_FILE.is_file():
    st.markdown(
        f"""
        <div style='display: flex; justify-content: center; align-items: center; margin-bottom: 20px;'>
            <img src='{LOGO_FILE.as_posix()}' style='max-width: 300px; height: auto;'/>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.warning("Logo not found. Make sure LOGO_PATH.png is in the same folder as app.py")

# ------------------------
# Session State
# ------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ------------------------
# Sidebar FAQs
# ------------------------
st.sidebar.header("FAQs")
FAQS = {
    "What is dementia?": "dementia",
    "What is Alzheimer’s disease?": "Alzheimer's disease",
    "What is Parkinson’s disease?": "Parkinson's disease",
    "What is ALS?": "Amyotrophic lateral sclerosis",
}

faq_choice = st.sidebar.radio("Choose a question:", list(FAQS.keys()), index=None)

# ------------------------
# Synonyms for detection
# ------------------------
CAUSE_SYNONYMS = ["cause", "causes", "etiology", "risk factor", "risk factors", "origin", "trigger", "triggers", "reason", "reasons", "mechanism"]
PREVENT_SYNONYMS = ["prevent", "prevention", "preventable", "avoiding", "prophylaxis", "treatment", "therapy", "management", "intervention", "reduce risk"]

# ------------------------
# Symptom categories
# ------------------------
SYMPTOM_CATEGORIES = {
    "memory": ["forgetting", "memory loss", "confusion", "disorientation", "alzheimer", "dementia"],
    "movement": ["tremor", "shaking", "stiffness", "rigidity", "parkinson", "motor impairment"],
    "speech": ["slurred speech", "dysarthria", "speech difficulty"],
    "vision": ["blurred vision", "double vision", "vision loss"],
    "swallowing": ["dysphagia", "difficulty swallowing"],
}

CATEGORY_CONDITIONS = {
    "memory": ["Dementia", "Alzheimer's disease", "Mild cognitive impairment"],
    "movement": ["Parkinson's disease", "Essential tremor", "Huntington's disease"],
    "speech": ["Stroke (medicine)", "ALS"],
    "vision": ["Stroke (medicine)", "Multiple sclerosis"],
    "swallowing": ["ALS", "Stroke (medicine)"],
}

MEDICAL_KEYWORDS = [
    "disease", "syndrome", "disorder", "condition", "medicine",
    "neurology", "psychiatry", "cardiology", "health", "medical",
    "pathology", "neurodegenerative", "infection"
]

# ------------------------
# What to do next helper
# ------------------------
def what_to_do_next():
    return (
        "\n\n**What to do next:**\n"
        "- Contact a healthcare professional for proper diagnosis and management.\n"
        "- Visit the **Resources page** on this website for guidance on what to ask your doctor, caregiving tips, and free brain exercises at home.\n"
        "- Follow safe, evidence-based routines to support cognitive health."
    )

# ------------------------
# Wikipedia Medical Query
# ------------------------
def get_wikipedia_answer(query):
    query_lower = query.lower()
    try:
        # Force medical stroke
        if "stroke" in query_lower:
            query = "Stroke (medicine)"

        # Search Wikipedia
        search_results = wikipedia.search(query, results=5)
        page = None

        query_keywords = set(query_lower.split())

        # Find the most specific medical page
        for result in search_results:
            try:
                p = wikipedia.page(result)
                title_lower = p.title.lower()
                content_lower = p.content.lower()

                # Check for medical content
                if not any(word in title_lower + content_lower for word in MEDICAL_KEYWORDS):
                    continue

                # Check if page matches all keywords in query
                match_score = sum(1 for kw in query_keywords if kw in title_lower or kw in content_lower)
                if match_score >= len(query_keywords) / 2:  # at least half keywords match
                    page = p
                    break
            except wikipedia.DisambiguationError as e:
                for option in e.options:
                    try:
                        p2 = wikipedia.page(option)
                        title_lower = p2.title.lower()
                        content_lower = p2.content.lower()
                        if not any(word in title_lower + content_lower for word in MEDICAL_KEYWORDS):
                            continue
                        match_score = sum(1 for kw in query_keywords if kw in title_lower or kw in content_lower)
                        if match_score >= len(query_keywords) / 2:
                            page = p2
                            break
                    except:
                        continue
            except:
                continue

        if not page:
            return "Sorry, I couldn’t find a medical answer for that." + what_to_do_next()

        # Split content by section
        sections = page.content.split("==")
        sections = [s.strip() for s in sections if s.strip()]

        # Cause detection
        if any(word in query_lower for word in CAUSE_SYNONYMS):
            for s in sections:
                if any(word in s.lower() for word in CAUSE_SYNONYMS):
                    return "**Cause:** " + " ".join(s.split(".")[:3]) + "." + what_to_do_next()
            return "**Cause (summary):** " + ". ".join(page.summary.split(".")[:3]) + "." + what_to_do_next()

        # Prevention / Management detection
        if any(word in query_lower for word in PREVENT_SYNONYMS):
            for s in sections:
                if any(word in s.lower() for word in PREVENT_SYNONYMS):
                    return "**Prevention / Management:** " + " ".join(s.split(".")[:3]) + "." + what_to_do_next()
            return "**Prevention / Management (summary):** " + ". ".join(page.summary.split(".")[:3]) + "." + what_to_do_next()

        # Default summary
        return page.summary[:900] + what_to_do_next()

    except Exception as e:
        return f"Error: {str(e)}" + what_to_do_next()

# ------------------------
# Symptom detection
# ------------------------
def detect_symptoms(text):
    matched_categories = []
    for category, keywords in SYMPTOM_CATEGORIES.items():
        if any(word in text.lower() for word in keywords):
            matched_categories.append(category)
    return matched_categories

def suggest_conditions(categories):
    conditions = []
    for cat in categories:
        conditions.extend(CATEGORY_CONDITIONS.get(cat, []))
    suggested = []
    for cond in set(conditions):
        try:
            summary = wikipedia.summary(cond, sentences=2)
            suggested.append(f"**{cond}:** {summary}")
        except:
            suggested.append(f"**{cond}:** Summary not found")
    return suggested

# ------------------------
# FAQ Response
# ------------------------
if faq_choice:
    answer = get_wikipedia_answer(FAQS[faq_choice])
    st.subheader(faq_choice)
    st.write(answer)
    st.session_state["messages"].append({"role": "assistant", "content": f"**{faq_choice}**\n{answer}"})

# ------------------------
# User Input
# ------------------------
user_query = st.text_input("Ask InMind anything:")

if user_query:
    st.session_state["messages"].append({"role": "user", "content": user_query})

    categories = detect_symptoms(user_query)
    if categories:
        suggestions = suggest_conditions(categories)
        response = "\n\n".join(suggestions) + what_to_do_next()
    else:
        response = get_wikipedia_answer(user_query)

    st.session_state["messages"].append({"role": "assistant", "content": response})

# ------------------------
# Display Chat History
# ------------------------
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**InMind:** {msg['content']}")

# ------------------------
# Clear Chat Button
# ------------------------
if st.button("Clear Chat"):
    st.session_state["messages"] = []
    st.experimental_rerun()

# ------------------------
# Disclaimer
# ------------------------
st.markdown(
    """
    <div style="text-align: center; margin-top: 30px; font-size: 13px; color: gray;">
         Disclaimer: InMind provides educational information only. It is not a substitute for professional medical advice.
    </div>
    """,
    unsafe_allow_html=True
)
