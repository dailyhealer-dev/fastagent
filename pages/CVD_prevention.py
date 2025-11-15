# CVD_prevention.py
import streamlit as st
import datetime
import sqlite3
from helper import llm, system_prompt

# ---------------------------- Helper Functions ----------------------------
def get_user_data(username):
    """
    Fetch user personal info, exercise, and nutrition data from SQLite database as a dictionary.
    """
    try:
        conn = sqlite3.connect("health_advisor.db")
        c = conn.cursor()

        # Personal info
        c.execute("SELECT * FROM personal_info WHERE username = ?", (username,))
        personal = c.fetchone()
        personal_cols = [desc[0] for desc in c.description] if personal else []
        personal_info = dict(zip(personal_cols, personal)) if personal else {}

        # Most recent exercise
        c.execute("""
            SELECT date, exercise_type, duration, intensity 
            FROM exercise_tracker 
            WHERE username = ? 
            ORDER BY date DESC LIMIT 1
        """, (username,))
        exercise = c.fetchone()
        exercise_cols = [desc[0] for desc in c.description] if exercise else []
        exercise_info = dict(zip(exercise_cols, exercise)) if exercise else {}

        # Most recent nutrition
        c.execute("""
            SELECT date, meal_type, calories, carbs, protein, fat 
            FROM nutrition_tracker 
            WHERE username = ? 
            ORDER BY date DESC LIMIT 1
        """, (username,))
        nutrition = c.fetchone()
        nutrition_cols = [desc[0] for desc in c.description] if nutrition else []
        nutrition_info = dict(zip(nutrition_cols, nutrition)) if nutrition else {}

        conn.close()
        return {"personal": personal_info, "exercise": exercise_info, "nutrition": nutrition_info}

    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return None

def calculate_bmi(weight, height_cm):
    """Calculate BMI using weight (kg) and height (cm)."""
    if height_cm and height_cm > 0:
        height_m = height_cm / 100
        return round(weight / (height_m ** 2), 2)
    return 0.0

# ---------------------------- Streamlit App ----------------------------
st.header("Cardiovascular Disease (CVD) Prevention Dashboard")

# ---------------------------- Username ----------------------------
if "username" not in st.session_state:
    st.session_state.username = None

if not st.session_state.username:
    st.subheader("Enter your username to get personalized guidance")
    username_input = st.text_input("Username")
    if st.button("Continue"):
        if username_input.strip():
            st.session_state.username = username_input.strip()
        else:
            st.warning("Please enter a valid username.")
else:
    username = st.session_state.username
    st.success(f"Welcome, {username}!")

    user_data = get_user_data(username)
    if not user_data or not user_data["personal"]:
        st.warning("No personal info found. Please enter your data in the Personal Info section first.")
    else:
        personal = user_data["personal"]
        exercise = user_data["exercise"]
        nutrition = user_data["nutrition"]

        age = personal.get("age", 35)
        sex = personal.get("gender", "Other")
        weight = personal.get("weight", 0)
        height = personal.get("height", 0)
        bmi = personal.get("bmi", calculate_bmi(weight, height))
        diet_quality = personal.get("diet", "Average")
        physical_activity = personal.get("physical_activity", "Moderate")

        # Summary
        st.markdown(f"""
        **Age:** {age} | **Sex:** {sex} | **BMI:** {bmi}  
        **Diet Quality:** {diet_quality} | **Activity Level:** {physical_activity}
        """)
        if exercise:
            st.info(f"Recent Exercise: {exercise.get('exercise_type', 'N/A')} ({exercise.get('duration', 'N/A')} min, Intensity: {exercise.get('intensity', 'N/A')})")
        if nutrition:
            st.info(f"Last Meal: {nutrition.get('meal_type', 'N/A')} | Calories: {nutrition.get('calories', 'N/A')} kcal")

        # ---------------------------- Tabs ----------------------------
        tab1, tab2, tab3, tab4 = st.tabs([
            "Preventive Advice",
            "Daily Health Tips",
            "Risk Awareness",
            "Progress Tracker"
        ])

        # ---------------------------- Tab 1: Preventive Advice ----------------------------
        with tab1:
            st.subheader("Personalized CVD Prevention Advice")
            condition = st.selectbox(
                "Select Condition for Preventive Advice",
                ["General Health", "Heart Disease Prevention", "Hypertension Prevention", "Stroke Prevention"],
                key="cvd_condition"
            )
            if st.button("Generate Prevention Advice"):
                prompt = f"""
                {system_prompt}
                Provide detailed, evidence-based prevention advice for {condition.lower()}.
                User is a {age}-year-old {sex} with BMI {bmi}, diet quality '{diet_quality}', 
                and activity level '{physical_activity}'. Recent exercise: {exercise.get('exercise_type', 'N/A')}.
                Recent meal: {nutrition.get('meal_type', 'N/A')} with {nutrition.get('calories', 'N/A')} kcal.
                Include diet, exercise, stress management, and routine check-up recommendations.
                """
                response = llm.invoke(prompt)
                st.markdown("### AI-Generated Prevention Guidance")
                st.markdown(response)

        # ---------------------------- Tab 2: Daily Health Tips ----------------------------
        with tab2:
            st.subheader("Daily Healthy Tips")
            if st.button("Generate Daily Tips"):
                today = datetime.date.today()
                prompt = f"""
                {system_prompt}
                Generate 3 short, actionable daily tips for preventing cardiovascular diseases 
                for a {age}-year-old {sex} with BMI {bmi}, diet quality '{diet_quality}', 
                and activity level '{physical_activity}'. Ensure each tip is actionable, realistic, 
                and promotes long-term heart health.
                """
                response = llm.invoke(prompt)
                st.markdown(f"### Tips for {today}")
                st.markdown(response)

        # ---------------------------- Tab 3: Risk Awareness ----------------------------
        with tab3:
            st.subheader("Learn About CVD Risk Factors")
            topic = st.selectbox(
                "Select a Topic",
                ["General Overview", "Heart Diseases", "Hypertension", "Stroke", "Atherosclerosis"]
            )
            if st.button("Learn More"):
                prompt = f"""
                {system_prompt}
                Provide a clear, evidence-based overview of {topic.lower()}, 
                its risk factors, early signs, and preventive measures. 
                Summarize using simple language suitable for public education.
                """
                response = llm.invoke(prompt)
                st.markdown(f"### {topic} Overview")
                st.markdown(response)

        # ---------------------------- Tab 4: AI-Driven Daily Prevention ----------------------------
        with tab4:
            st.subheader("Daily AI-Driven Prevention Insights")
            today = str(datetime.date.today())

            if "cvd_tracker" not in st.session_state:
                st.session_state["cvd_tracker"] = {}

            if today not in st.session_state["cvd_tracker"]:
                # Generate 7 AI-driven prevention tips based on recent data
                prompt = f"""
                {system_prompt}
                Generate 7 personalized daily cardiovascular prevention tips for a {age}-year-old {sex} 
                with BMI {bmi}, diet quality '{diet_quality}', activity level '{physical_activity}'. 
                Recent exercise: {exercise.get('exercise_type', 'N/A')} ({exercise.get('duration', 'N/A')} min). 
                Recent meal: {nutrition.get('meal_type', 'N/A')} ({nutrition.get('calories', 'N/A')} kcal). 
                Return tips as a numbered list.
                """
                tips_response = llm.invoke(prompt)
                # Split tips into list
                tips_list = [tip.strip() for tip in tips_response.split("\n") if tip.strip()]
                st.session_state["cvd_tracker"][today] = {tip: False for tip in tips_list}

            st.markdown(f"### Progress for {today}")
            completed_today = st.session_state["cvd_tracker"][today]

            for tip in completed_today:
                if st.checkbox(tip, value=completed_today[tip], key=f"{today}_{tip}"):
                    completed_today[tip] = True

            # Summary
            total = len(completed_today)
            completed_count = sum(completed_today.values())
            if completed_count == total:
                st.success("✅ You’ve completed all your AI-recommended daily prevention tips!")
            else:
                st.info(f"You’ve completed {completed_count} of {total} AI-recommended daily tips.")

# ---------------------------- Disclaimer ----------------------------
st.markdown("---")
st.caption(
    "Disclaimer: This AI assistant provides educational guidance only. "
    "It does not replace professional medical advice. Consult your doctor for personalized care."
)
