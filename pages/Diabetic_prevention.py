# Diabetic_Prevention.py
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

        # Fetch personal info
        c.execute("SELECT * FROM personal_info WHERE username = ?", (username,))
        personal = c.fetchone()
        personal_cols = [desc[0] for desc in c.description] if personal else []
        personal_info = dict(zip(personal_cols, personal)) if personal else {}

        # Fetch most recent exercise record
        c.execute("""
            SELECT date, exercise_type, duration, intensity 
            FROM exercise_tracker 
            WHERE username = ? 
            ORDER BY date DESC LIMIT 1
        """, (username,))
        exercise = c.fetchone()
        exercise_cols = [desc[0] for desc in c.description] if exercise else []
        exercise_info = dict(zip(exercise_cols, exercise)) if exercise else {}

        # Fetch most recent nutrition record
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

        return {
            "personal": personal_info,
            "exercise": exercise_info,
            "nutrition": nutrition_info
        }

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
st.header("🩺 Diabetes Prevention Dashboard")

# ---------------------------- Step 1: Ask for Username ----------------------------
if "username" not in st.session_state:
    st.session_state.username = None

if not st.session_state.username:
    st.subheader("Enter your username to get personalized advice")
    username_input = st.text_input("Username")
    if st.button("Continue"):
        if username_input.strip():
            st.session_state.username = username_input.strip()
        else:
            st.warning("Please enter a valid username.")
else:
    username = st.session_state.username
    st.success(f"Welcome, {username}!")

    # ---------------------------- Fetch User Data ----------------------------
    user_data = get_user_data(username)

    if not user_data or not user_data["personal"]:
        st.warning("No personal info found. Please enter your data in the Personal Info section first.")
    else:
        personal = user_data["personal"]
        exercise = user_data["exercise"]
        nutrition = user_data["nutrition"]

        # Extract details
        age = personal.get("age", 35)
        sex = personal.get("gender", "Other")
        weight = personal.get("weight", 0)
        height = personal.get("height", 0)
        bmi = personal.get("bmi", calculate_bmi(weight, height))
        diet_quality = personal.get("diet", "Average")
        activity_level = personal.get("physical_activity", "Moderate")
        family_history = personal.get("family_history", "No")

        # Display Summary
        st.markdown(f"""
        **Age:** {age} | **Sex:** {sex} | **BMI:** {bmi}  
        **Diet Quality:** {diet_quality} | **Activity Level:** {activity_level} | **Family History:** {family_history}
        """)

        if exercise:
            st.info(f"Recent Exercise: {exercise.get('exercise_type', 'N/A')} ({exercise.get('duration', 'N/A')} min, Intensity: {exercise.get('intensity', 'N/A')})")

        if nutrition:
            st.info(f"Last Meal: {nutrition.get('meal_type', 'N/A')} | Calories: {nutrition.get('calories', 'N/A')} kcal")

        # ---------------------------- Tabs ----------------------------
        tab1, tab2, tab3, tab4 = st.tabs([
            "Risk Assessment", 
            "Lifestyle Guidance", 
            "Daily Prevention Tips", 
            "Progress Tracker"
        ])

        # ---------------------------- Tab 1: Risk Assessment ----------------------------
        with tab1:
            st.subheader("Risk Assessment")
            st.markdown(f"**Age:** {age}, **BMI:** {bmi}, **Family History:** {family_history}")
            st.markdown(f"**Activity Level:** {activity_level}, **Diet Quality:** {diet_quality}")

            if st.button("Analyze Risk"):
                prompt = f"""
                {system_prompt}
                Assess diabetes risk for a {age}-year-old {sex} with BMI {bmi},
                family history: {family_history}, physical activity level: {activity_level}, 
                and diet quality: {diet_quality}. 
                Provide a short summary of potential risk and prevention recommendations.
                """
                response = llm.invoke(prompt)
                st.markdown("### Risk Assessment Result")
                st.markdown(response)

        # ---------------------------- Tab 2: Lifestyle Guidance ----------------------------
        with tab2:
            st.subheader("Lifestyle and Nutrition Guidance")
            focus_area = st.selectbox(
                "Choose Focus Area", 
                ["Dietary Improvement", "Physical Activity", "Weight Management", "Sleep and Stress Control"]
            )
            if st.button("Get Lifestyle Guidance"):
                prompt = f"""
                {system_prompt}
                Provide personalized lifestyle and nutrition guidance for diabetes prevention 
                for the user {username} focusing on {focus_area}.
                Include practical steps and evidence-based recommendations suitable for adults.
                """
                response = llm.invoke(prompt)
                st.markdown("### Lifestyle Guidance")
                st.markdown(response)

        # ---------------------------- Tab 3: Daily Prevention Tips ----------------------------
        with tab3:
            st.subheader("Daily Diabetes Prevention Tips")
            if st.button("Generate Daily Tips"):
                today = datetime.date.today()
                prompt = f"""
                {system_prompt}
                Generate 3 concise, actionable daily tips for preventing diabetes for a {age}-year-old {sex}. 
                Ensure the tips are practical for everyday life and evidence-based.
                """
                response = llm.invoke(prompt)
                st.markdown(f"### Tips for {today}")
                st.markdown(response)

        # ---------------------------- Tab 4: AI-Driven Progress Tracker ----------------------------
        with tab4:
            st.subheader("Daily Prevention Progress")
            
            if "diabetes_tracker" not in st.session_state:
                st.session_state["diabetes_tracker"] = {}
            
            today = str(datetime.date.today())

            # Generate AI-driven prevention activities if not already generated
            if today not in st.session_state["diabetes_tracker"]:
                prompt = f"""
                {system_prompt}
                Generate 5-7 daily diabetes prevention activities for a {age}-year-old {sex} 
                with BMI {bmi}, diet quality '{diet_quality}', activity level '{activity_level}'. 
                Recent exercise: {exercise.get('exercise_type', 'N/A')} ({exercise.get('duration', 'N/A')} min). 
                Recent meal: {nutrition.get('meal_type', 'N/A')} ({nutrition.get('calories', 'N/A')} kcal). 
                Return the activities as a numbered list.
                """
                response = llm.invoke(prompt)
                activities = [line.strip() for line in response.split("\n") if line.strip()]
                st.session_state["diabetes_tracker"][today] = {act: False for act in activities}

            # Display activities as checkboxes
            st.markdown(f"### Progress for {today}")
            today_activities = st.session_state["diabetes_tracker"][today]
            for act in today_activities:
                today_activities[act] = st.checkbox(act, value=today_activities[act], key=f"{today}_{act}")

            # Show progress summary
            total = len(today_activities)
            completed_count = sum(today_activities.values())
            if completed_count == total:
                st.success("✅ You've completed all your daily prevention activities!")
            else:
                st.info(f"You’ve completed {completed_count} of {total} daily prevention activities.")

            st.markdown(
                "Your progress is saved locally for this session. Checking activities helps you stay accountable!"
            )

# ---------------------------- Disclaimer ----------------------------
st.markdown("---")
st.caption(
    "Disclaimer: This AI assistant provides educational guidance only. "
    "It does not replace professional medical advice. Consult your doctor for personalized care."
)
