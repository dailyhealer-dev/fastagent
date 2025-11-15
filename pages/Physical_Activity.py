# physical_activity_dashboard.py
import streamlit as st
import sqlite3
import datetime
from agents.physical_activity_agent import get_physical_activity_response

# ---------------------------- Helper Functions ----------------------------
def get_user_data(username):
    """
    Fetch personal info and latest physical activity from database.
    """
    try:
        conn = sqlite3.connect("health_advisor.db")
        c = conn.cursor()

        # Fetch personal info
        c.execute("SELECT age, gender, physical_activity FROM personal_info WHERE username = ?", (username,))
        personal = c.fetchone()
        personal_info = dict(zip([desc[0] for desc in c.description], personal)) if personal else {}

        # Fetch latest exercise record
        c.execute("""
            SELECT date, exercise_type, duration, intensity 
            FROM exercise_tracker 
            WHERE username = ? 
            ORDER BY date DESC LIMIT 1
        """, (username,))
        exercise = c.fetchone()
        exercise_info = dict(zip([desc[0] for desc in c.description], exercise)) if exercise else {}

        return {
            "personal": personal_info,
            "exercise": exercise_info
        }
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return None
    finally:
        conn.close()

# ---------------------------- Streamlit App ----------------------------
st.header("🏃 Physical Activity Dashboard")

# ---------------------------- Step 1: Ask for Username ----------------------------
if "username" not in st.session_state:
    st.session_state.username = None

if not st.session_state.username:
    st.subheader("Enter your username to fetch activity data")
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

        age = personal.get("age", 30)
        sex = personal.get("gender", "Other")
        recent_activity = exercise.get("exercise_type", "N/A")
        recent_duration = exercise.get("duration", "N/A")
        recent_intensity = exercise.get("intensity", "N/A")

        # ---------------------------- Tabs ----------------------------
        tab1, tab2, tab3, tab4 = st.tabs([
            "Activity Summary",
            "AI Exercise Recommendations",
            "Daily Tips & Tracker",
            "History & Insights"
        ])

        # ---------------------------- Tab 1: Activity Summary ----------------------------
        with tab1:
            st.subheader("Your Recent Physical Activity")
            st.markdown(f"**Age:** {age} | **Sex:** {sex}")
            st.markdown(f"**Last Exercise:** {recent_activity} ({recent_duration} min, Intensity: {recent_intensity})")
            st.markdown(f"**Average Physical Activity Level:** {personal.get('physical_activity', 'Moderate')}")

        # ---------------------------- Tab 2: AI Exercise Recommendations ----------------------------
        with tab2:
            st.subheader("AI-Generated Exercise Recommendations")
            condition = st.selectbox(
                "Health Condition (Optional)", 
                ["None", "Hypertension", "Diabetes", "Arthritis"], 
                key="pa_condition_tab2"
            )
            goal = st.selectbox(
                "Fitness Goal", 
                ["General Health", "Strength", "Endurance", "Balance", "Flexibility"], 
                key="pa_goal_tab2"
            )

            if st.button("Get Recommendations", key="pa_recommend_btn_tab2"):
                query = (
                    f"Provide personalized exercise recommendations for a {age}-year-old {sex} "
                    f"with {condition}, focusing on {goal}. Include practical daily tips and simple exercises."
                )
                recommendation = get_physical_activity_response(query)
                st.markdown("### AI Exercise Guidance")
                st.markdown(recommendation)

        # ---------------------------- Tab 3: Daily Tips & Tracker ----------------------------
        with tab3:
            st.subheader("Daily Physical Activity Tips & Tracker")
            today = str(datetime.date.today())

            if "exercise_tracker_today" not in st.session_state:
                st.session_state["exercise_tracker_today"] = {}

            if today not in st.session_state["exercise_tracker_today"]:
                # Generate AI-driven daily tips
                query_tips = (
                    f"Generate 5 actionable daily physical activity tips for a {age}-year-old {sex} "
                    f"considering recent activity '{recent_activity}' ({recent_duration} min, Intensity: {recent_intensity})."
                )
                tips_response = get_physical_activity_response(query_tips)
                # Split into individual tips for checkboxes
                tips_list = [line.strip() for line in tips_response.split("\n") if line.strip()]
                st.session_state["exercise_tracker_today"][today] = {tip: False for tip in tips_list}

            st.markdown(f"### Tips for {today}")
            today_tips = st.session_state["exercise_tracker_today"][today]
            for tip in today_tips:
                today_tips[tip] = st.checkbox(tip, value=today_tips[tip], key=f"{today}_{tip}")

            total = len(today_tips)
            completed_count = sum(today_tips.values())
            if completed_count == total and total > 0:
                st.success("✅ You’ve completed all daily exercise activities!")
            else:
                st.info(f"You’ve completed {completed_count} of {total} activities.")

        # ---------------------------- Tab 4: History & Insights ----------------------------
        with tab4:
            st.subheader("Exercise History & Insights")
            if exercise:
                st.markdown(f"**Most Recent Exercise:** {recent_activity}")
                st.markdown(f"**Duration:** {recent_duration} min")
                st.markdown(f"**Intensity:** {recent_intensity}")
                st.markdown(f"**Date:** {exercise.get('date', 'N/A')}")
            else:
                st.info("No exercise history found.")

            insights_query = st.text_area("Ask a question about physical activity (e.g., benefits, exercises, routines)")
            if st.button("Get Insight", key="pa_insight_btn"):
                response = get_physical_activity_response(insights_query)
                st.markdown("### AI Insight")
                st.markdown(response)

# ---------------------------- Disclaimer ----------------------------
st.markdown("---")
st.caption(
    "Disclaimer: This AI assistant provides educational guidance only. "
    "It does not replace professional medical advice. Consult a certified fitness professional for personalized exercise plans."
)