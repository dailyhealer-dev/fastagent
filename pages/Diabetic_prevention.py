import streamlit as st
from helper import llm, system_prompt
import datetime

# ----------------------------
# Page Configuration
# ----------------------------
st.header("Diabetes Prevention Dashboard")

st.markdown("""
This dashboard helps individuals understand evidence-based strategies to prevent or manage the risk of diabetes 
through lifestyle changes, diet, and regular monitoring. The insights are generated using IBM’s Granite Foundation Model.
""")

# ----------------------------
# Tabs for Organized Layout
# ----------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Risk Assessment", 
    "Lifestyle Guidance", 
    "Daily Prevention Tips", 
    "Progress Tracker"
])

# ----------------------------
# Tab 1: Risk Assessment
# ----------------------------
with tab1:
    st.subheader("Risk Assessment")

    age = st.number_input("Age", min_value=1, max_value=120, value=30, key="db_age")
    bmi = st.number_input("BMI (Body Mass Index)", min_value=10.0, max_value=60.0, value=22.5, key="db_bmi")
    family_history = st.selectbox("Family History of Diabetes", ["No", "Yes"], key="db_family")
    activity_level = st.selectbox("Physical Activity Level", ["Low", "Moderate", "High"], key="db_activity")
    diet_quality = st.selectbox("Diet Quality", ["Poor", "Average", "Healthy"], key="db_diet")

    if st.button("Analyze Risk", key="db_risk_button"):
        prompt = f"""
        {system_prompt}
        Assess diabetes risk for a {age}-year-old individual with a BMI of {bmi},
        family history: {family_history}, physical activity level: {activity_level}, 
        and diet quality: {diet_quality}. 
        Provide a short summary of potential risk and prevention recommendations.
        """
        response = llm.invoke(prompt)
        st.text_area("Risk Assessment Result", response, height=200)

# ----------------------------
# Tab 2: Lifestyle Guidance
# ----------------------------
with tab2:
    st.subheader("Lifestyle and Nutrition Guidance")

    focus_area = st.selectbox(
        "Choose Focus Area", 
        ["Dietary Improvement", "Physical Activity", "Weight Management", "Sleep and Stress Control"], 
        key="db_focus"
    )

    if st.button("Get Lifestyle Guidance", key="db_guidance_button"):
        prompt = f"""
        {system_prompt}
        Provide personalized lifestyle and nutrition guidance for diabetes prevention focusing on {focus_area}.
        Include practical steps and evidence-based recommendations suitable for adults.
        """
        response = llm.invoke(prompt)
        st.text_area("Lifestyle Guidance", response, height=220)

# ----------------------------
# Tab 3: Daily Prevention Tips
# ----------------------------
with tab3:
    st.subheader("Daily Diabetes Prevention Tips")

    if st.button("Generate Daily Tips", key="db_tips_button"):
        today = datetime.date.today()
        prompt = f"""
        {system_prompt}
        Generate 3 concise, actionable daily tips for preventing diabetes. 
        Ensure the tips are practical for everyday life and evidence-based.
        """
        response = llm.invoke(prompt)
        st.text_area(f"Tips for {today}", response, height=150)

# ----------------------------
# Tab 4: Progress Tracker
# ----------------------------
with tab4:
    st.subheader("Progress Tracker")

    if "diabetes_tracker" not in st.session_state:
        st.session_state["diabetes_tracker"] = {}

    today = datetime.date.today()
    done_today = st.session_state["diabetes_tracker"].get(str(today), False)

    if done_today:
        st.info("You have already logged your prevention activities for today.")
    else:
        if st.button("Mark Today's Prevention Activities as Done", key="db_mark_done"):
            st.session_state["diabetes_tracker"][str(today)] = True
            st.success("Today's prevention activities have been logged successfully.")

    st.markdown("Your daily progress is stored locally for this session to help you maintain accountability.")

st.markdown("---")
st.caption(
    "Disclaimer: This AI assistant provides educational guidance only. "
    "It does not replace professional medical advice. Consult your doctor for personalized care."
)