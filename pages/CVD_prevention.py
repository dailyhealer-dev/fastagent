# NCD_prevention.py
import streamlit as st
import datetime
import logging
from helper import llm, system_prompt

# ---------------------------------------
# Page Configuration
# ---------------------------------------
st.header("Cardiovascular Disease (CVD) Prevention Dashboard")

# ---------------------------------------
# User Inputs
# ---------------------------------------
st.subheader("Personal Information")
col1, col2, col3 = st.columns(3)

with col1:
    age = st.number_input("Age", min_value=0, max_value=120, value=35, key="ncd_age")

with col2:
    sex = st.selectbox("Sex", ["Male", "Female", "Other"], key="ncd_sex")

with col3:
    risk_factors = st.multiselect(
        "Select Known Risk Factors (if any)",
        ["Smoking", "Physical Inactivity", "Unhealthy Diet", "High Blood Pressure", "Obesity", "Diabetes", "None"],
        default=["None"],
        key="ncd_risk_factors"
    )

# ---------------------------------------
# Tabs for Dashboard Sections
# ---------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Preventive Advice",
    "Daily Health Tips",
    "Risk Awareness",
    "Health Tracker"
])

# ---------------------------------------
# Tab 1: Preventive Advice
# ---------------------------------------
with tab1:
    st.subheader("Personalized CVD Prevention Advice")
    condition = st.selectbox(
        "Select Condition for Preventive Advice",
        ["General Health", "Heart Disease Prevention", "Hypertension Prevention", "Stroke Prevention"],
        key="ncd_condition"
    )

    if st.button("Generate Prevention Advice", key="ncd_advice_btn"):
        query = (
            f"Provide detailed lifestyle-based prevention advice for {condition.lower()} "
            f"for a {age}-year-old {sex} with risk factors: {', '.join(risk_factors)}. "
            "Include diet, exercise, stress management, and screening recommendations."
        )
        try:
            prompt = f"{system_prompt}\nUser: {query}\nAssistant:"
            logging.info("Generating prevention advice using IBM Granite LLM...")
            result = llm.generate([prompt])
            answer = result.generations[0][0].text.strip()
            st.text_area("AI-Generated Prevention Guidance", answer, height=220)
        except Exception as e:
            logging.error(f"Error generating prevention advice: {e}")
            st.error("Unable to generate advice at this time. Please try again later.")

# ---------------------------------------
# Tab 2: Daily Health Tips
# ---------------------------------------
with tab2:
    st.subheader("Daily Lifestyle Tips")
    if st.button("Generate Daily Tips", key="ncd_tips_btn"):
        query_tips = (
            f"Generate 3 short, practical daily tips for preventing Cardio-vascular diseases "
            f"for a {age}-year-old {sex} with risk factors: {', '.join(risk_factors)}. "
            "Focus on nutrition, movement, hydration, and stress reduction."
        )
        try:
            prompt_tips = f"{system_prompt}\nUser: {query_tips}\nAssistant:"
            result = llm.generate([prompt_tips])
            tips = result.generations[0][0].text.strip()
            st.text_area("AI Daily Tips", tips, height=150)
        except Exception as e:
            logging.error(f"Error generating daily tips: {e}")
            st.error("Could not fetch daily tips. Try again later.")

# ---------------------------------------
# Tab 3: Risk Awareness
# ---------------------------------------
with tab3:
    st.subheader("Learn About CVD Risk Factors")
    ncd_type = st.selectbox(
        "Select a Disease Category",
        ["General Overview", "Heart Diseases", "Hypertension", "Stroke", "Atherosclerosis"],
        key="ncd_info_select"
    )

    if st.button("Learn More", key="ncd_learn_btn"):
        query_info = (
            f"Provide a clear, evidence-based overview of {ncd_type.lower()}, "
            "its major risk factors, early signs, and prevention strategies. "
            "Summarize using simple public health language."
        )
        try:
            prompt_info = f"{system_prompt}\nUser: {query_info}\nAssistant:"
            result = llm.generate([prompt_info])
            info = result.generations[0][0].text.strip()
            st.text_area("Educational Overview", info, height=250)
        except Exception as e:
            logging.error(f"Error generating risk overview: {e}")
            st.error("Unable to retrieve information at this time.")

# ---------------------------------------
# Tab 4: Health Tracker
# ---------------------------------------
with tab4:
    st.subheader("Track Your Prevention Progress")

    today = datetime.date.today()
    if "ncd_prevention_done" not in st.session_state:
        st.session_state["ncd_prevention_done"] = {}

    done_today = st.session_state["ncd_prevention_done"].get(str(today), False)

    if done_today:
        st.info("You have logged today's healthy activity.")
    else:
        if st.button("Mark Today's Prevention Activity as Done", key="ncd_done_btn"):
            st.session_state["ncd_prevention_done"][str(today)] = True
            st.success("Today's prevention activity logged successfully!")

    st.markdown("---")
    st.caption("Tip: Consistency in daily routines is the foundation of NCD prevention.")

# ---------------------------------------
# Footer
# ---------------------------------------
st.markdown("---")
st.caption(
    "Disclaimer: This AI assistant provides educational guidance only. "
    "It does not replace professional medical advice. Consult your doctor for personalized care."
) 