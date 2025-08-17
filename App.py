import streamlit as st

# -------------------------------
# InMind: Neurodegenerative Risk Assistant
# -------------------------------

st.set_page_config(page_title="InMind – Early Screening", layout="centered")

st.title("🧠 InMind: Neurodegenerative Screening Tool")
st.write("""
This tool is designed to **help families and individuals recognize potential early signs of neurodegenerative disease**.
It does not provide medical diagnoses. For medical concerns, please consult a licensed physician.
""")

# -------------------------------
# Symptom Checklist
# -------------------------------
st.header("1. Select Observed Symptoms")

symptoms = {
    "Memory Loss": st.checkbox("Frequent memory lapses or confusion"),
    "Speech Difficulty": st.checkbox("Difficulty finding words or following conversations"),
    "Movement Issues": st.checkbox("Tremors, stiffness, or slowed movements"),
    "Mood Changes": st.checkbox("Noticeable mood swings, depression, or anxiety"),
    "Disorientation": st.checkbox("Difficulty recognizing places, people, or time"),
    "Sleep Problems": st.checkbox("Disturbed sleep or vivid dreams"),
    "Fine Motor Decline": st.checkbox("Trouble with handwriting, buttoning clothes, or small tasks"),
    "Judgment Issues": st.checkbox("Poor decision-making or risky behavior"),
}

selected_symptoms = [k for k, v in symptoms.items() if v]

# -------------------------------
# Analysis
# -------------------------------
if st.button("Analyze Symptoms"):
    if not selected_symptoms:
        st.warning("Please select at least one symptom to continue.")
    else:
        st.subheader("2. Preliminary Insights")

        # Very simple "inference engine"
        if "Memory Loss" in selected_symptoms and "Disorientation" in selected_symptoms:
            st.write("🔎 The symptoms suggest possible **early Alzheimer's-type changes**.")
            likely_next = ["Speech Difficulty", "Judgment Issues"]
        elif "Movement Issues" in selected_symptoms and "Sleep Problems" in selected_symptoms:
            st.write("🔎 The symptoms may align with **Parkinson’s-related changes**.")
            likely_next = ["Fine Motor Decline", "Mood Changes"]
        elif "Speech Difficulty" in selected_symptoms and "Mood Changes" in selected_symptoms:
            st.write("🔎 The symptoms may be consistent with **Frontotemporal Degeneration (FTD)**.")
            likely_next = ["Judgment Issues", "Disorientation"]
        else:
            st.write("🔎 The current pattern does not clearly match a specific condition, but monitoring is advised.")
            likely_next = ["Track any changes over the next 3–6 months"]

        # Show possible future symptoms
        st.subheader("3. What to Watch For")
        for n in likely_next:
            st.write(f"• {n}")

        # Next steps
        st.subheader("4. Recommended Next Steps")
        st.write("""
        - Schedule a neurological or cognitive screening with a physician.  
        - Begin keeping a **symptom diary**: note changes, frequency, and severity.  
        - Explore lifestyle measures: sleep hygiene, exercise, cognitive stimulation, and diet.  
        - Share observations with close family members for early planning.  
        - If symptoms worsen, request referral to a neurologist.  
        """)

# -------------------------------
# Disclaimer
# -------------------------------
st.markdown("---")
st.caption("Disclaimer: This tool is for educational purposes only and not a medical diagnosis. Always consult a healthcare provider for medical advice.")
