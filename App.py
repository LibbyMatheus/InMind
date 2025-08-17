# app.py
import streamlit as st
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
import joblib

st.set_page_config(page_title="InMind Early Check", layout="centered")

# ---- Header & Disclaimer ----
st.title("InMind — Early Brain Health Check (Prototype)")
st.markdown(
"""
**Disclaimer:** This tool is a prototype screening aid for educational purposes only.
It is *not* a medical diagnostic device. Results should never replace clinical evaluation.
If you or a loved one have concerning symptoms, contact a licensed healthcare professional.
"""
)

# ---- Collect basic info ----
st.header("Step 1 — Basic information")
age = st.number_input("Age", min_value=18, max_value=120, value=65)
sex = st.selectbox("Sex assigned at birth", ["Female", "Male", "Other / Prefer not to say"])

# ---- Symptom checklist ----
st.header("Step 2 — Symptom checklist (check all that apply)")
symptoms = {
    "memory_recent": "Noticeable recent memory lapses (forgetting recent conversations or events)",
    "difficulty_tasks": "Difficulty planning or completing familiar tasks",
    "disorientation": "Disorientation in time or place",
    "language": "Trouble finding words or following conversations",
    "mood_change": "Marked mood or personality changes",
    "motor_symptoms": "Tremors, stiffness, or slowed movement",
    "visual_spatial": "Difficulty with spatial tasks (driving, judging distances)",
    "sleep_problems": "Marked changes in sleep patterns (insomnia, vivid dreams)",
    "smell_loss": "Noticeable loss of sense of smell (anosmia)",
}

symptom_input = {}
for key, label in symptoms.items():
    symptom_input[key] = int(st.checkbox(label))

# ---- Simple risk score (interpretable) ----
st.header("Step 3 — Screening result")
# Rule-based scoring, weighted by symptom type and age
weights = {
    "memory_recent": 3,
    "difficulty_tasks": 2,
    "disorientation": 3,
    "language": 2,
    "mood_change": 1,
    "motor_symptoms": 2,
    "visual_spatial": 1,
    "sleep_problems": 1,
    "smell_loss": 1,
}
score = sum(symptom_input[k]*w for k,w in weights.items())
age_factor = 0
if age >= 65:
    age_factor = 2
elif age >= 50:
    age_factor = 1
score += age_factor

# Convert to probability (placeholder logistic mapping)
# If a saved trained model exists, use it. Otherwise, use simple mapping.
MODEL_PATH = "placeholder_model.joblib"

def heuristic_probability(s):
    # maps numeric score to a probability in [0,1]
    # tuned conservatively for prototype
    p = 1 / (1 + np.exp(-(s - 5)/2.0))
    return float(p)

prob = heuristic_probability(score)
risk_band = "Low"
if prob >= 0.7:
    risk_band = "High"
elif prob >= 0.35:
    risk_band = "Moderate"

st.metric(label=f"Estimated risk ({risk_band})", value=f"{prob*100:.0f}%")

# ---- Inference: likely next symptoms based on checked items ----
st.header("Possible symptoms to monitor next")
inferred = []
if symptom_input["memory_recent"] or symptom_input["difficulty_tasks"]:
    inferred += [
        "Increased difficulty with short-term memory (e.g., forgetting appointments)",
        "Reduced ability to manage finances or medications"
    ]
if symptom_input["motor_symptoms"]:
    inferred += [
        "Progression in motor symptoms: slowed movement, increased stiffness",
        "Greater difficulty with balance"
    ]
if symptom_input["smell_loss"]:
    inferred += [
        "Potential earlier olfactory changes; monitor for related cognitive issues"
    ]
if not inferred:
    inferred = ["No strong additional symptom trajectory inferred from current inputs. Continue routine monitoring."]

for i in inferred:
    st.write("- " + i)

# ---- Next steps (actionable, safe) ----
st.header("Recommended next steps (evidence-based & cautious)")
st.write("""
1. **Schedule a clinical evaluation** — bring this report to a primary care physician or neurologist.  
2. **Bring a companion** to appointments to help recall history and symptoms.  
3. **Ask about standard cognitive tests** (e.g., MMSE, MoCA) and whether a referral for imaging or specialist assessment is appropriate.  
4. **Document changes**: keep a short diary of symptoms, dates, and impact on daily life.  
5. **Immediate red flags**: seek urgent care if there is sudden confusion, focal weakness, sudden vision loss, or loss of speech.
""")

# ---- Provide downloadable report ----
if st.button("Generate brief report (PDF/Copy)"):
    # simple text report for now
    report = f"InMind Early Check Report\nAge: {age}\nSex: {sex}\nRisk: {risk_band} ({prob*100:.0f}%)\nChecked symptoms:\n"
    for k,v in symptom_input.items():
        if v:
            report += f"- {symptoms[k]}\n"
    report += "\nInferred next symptoms:\n"
    for s in inferred:
        report += f"- {s}\n"
    report += "\nNext steps: Seek clinical evaluation. This is not a diagnosis."
    st.text_area("Report (copy/paste):", value=report, height=300)

# ---- Footer: resources and citations ----
st.markdown("---")
st.markdown("**Resources:** National Institutes of Health, Alzheimer's Association, and other clinical resources. For more, visit the InMind resources page.")
