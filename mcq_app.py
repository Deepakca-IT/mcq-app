import streamlit as st
import pandas as pd
import os
import random
from datetime import datetime

@st.cache_data
def load_questions():
    return pd.read_csv("questions.csv")

@st.cache_data
def load_scores():
    if os.path.exists("scores.csv"):
        return pd.read_csv("scores.csv")
    else:
        return pd.DataFrame(columns=["email", "username", "date", "score", "total", "wrong_questions"])

def save_score(email, username, score, total, wrong_questions):
    date = datetime.now().strftime("%Y-%m-%d")
    scores = load_scores()
    scores = pd.concat([
        scores,
        pd.DataFrame([{
            "email": email,
            "username": username,
            "date": date,
            "score": score,
            "total": total,
            "wrong_questions": ";".join(wrong_questions)
        }])
    ], ignore_index=True)
    scores.to_csv("scores.csv", index=False)

def admin_panel():
    st.title("Admin Panel")
    uploaded_file = st.file_uploader("Upload CSV to add questions", type=["csv"])
    if uploaded_file is not None:
        df_new = pd.read_csv(uploaded_file)
        df_old = load_questions()
        df_combined = pd.concat([df_old, df_new], ignore_index=True)
        df_combined.to_csv("questions.csv", index=False)
        st.success("Questions updated successfully!")
    st.write("Current Questions:")
    st.dataframe(load_questions())

def mcq_test():
    st.title("Daily MCQ Test")
    email = st.text_input("Enter your email ID")
    username = st.text_input("Enter your name")

    if email and username:
        if st.button("View My Progress"):
            scores = load_scores()
            user_scores = scores[scores["email"] == email]
            if not user_scores.empty:
                st.subheader("Your Progress History")
                st.dataframe(user_scores.sort_values("date", ascending=False))
                chart_data = user_scores[["date", "score"]].set_index("date")
                st.line_chart(chart_data)
            else:
                st.info("No records found for this email.")
            st.stop()

        questions = load_questions()
        daily_questions = questions[questions['tag'] == 'daily']

        if "questions_order" not in st.session_state:
            st.session_state.questions_order = random.sample(range(len(daily_questions)), len(daily_questions))
            st.session_state.current_index = 0
            st.session_state.score = 0
            st.session_state.user_answers = []
            st.session_state.selected_option = None
            st.session_state.quiz_ended = False
            st.session_state.wrong_questions = []

        if st.session_state.quiz_ended:
            st.success(f"{username}, your score is {st.session_state.score}/{len(st.session_state.questions_order)}")
            st.subheader("Quiz Summary")
            for i, index in enumerate(st.session_state.questions_order):
                row = daily_questions.iloc[index]
                st.markdown(f"**Q{i+1}: {row['question']}**")
                st.markdown(f"Your Answer: {st.session_state.user_answers[i]}")
                st.markdown(f"Correct Answer: {row['answer']}")
                st.markdown(f"Explanation: {row['explanation']}")
                st.markdown("---")
            if st.button("Restart Quiz"):
                for key in ["questions_order", "current_index", "score", "user_answers", "selected_option", "quiz_ended", "wrong_questions"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.stop()
            return

        index = st.session_state.questions_order[st.session_state.current_index]
        row = daily_questions.iloc[index]

        st.subheader(f"Q{st.session_state.current_index + 1}: {row['question']}")
        options = [row['option1'], row['option2'], row['option3'], row['option4']]

        if st.session_state.selected_option is None:
            for option in options:
                if st.button(option):
                    st.session_state.selected_option = option
                    st.session_state.user_answers.append(option)
                    if option == row['answer']:
                        st.session_state.score += 1
                    else:
                        st.session_state.wrong_questions.append(row['question'])
        else:
            for option in options:
                if option == row['answer']:
                    st.markdown(f"<div style='color: green; font-weight: bold'>{option}</div>", unsafe_allow_html=True)
                elif option == st.session_state.selected_option:
                    st.markdown(f"<div style='color: red; font-weight: bold'>{option}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(option)
            st.info(f"Explanation: {row['explanation']}")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.session_state.selected_option and st.button("Next"):
                st.session_state.current_index += 1
                st.session_state.selected_option = None
                if st.session_state.current_index >= len(st.session_state.questions_order):
                    st.session_state.quiz_ended = True
                    save_score(email, username, st.session_state.score, len(st.session_state.questions_order), st.session_state.wrong_questions)
                    st.stop()
        with col2:
            if st.session_state.selected_option and st.button("End Quiz"):
                st.session_state.quiz_ended = True
                save_score(email, username, st.session_state.score, len(st.session_state.questions_order), st.session_state.wrong_questions)
                st.stop()

def main():
    st.sidebar.title("Navigation")
    menu = st.sidebar.radio("Go to", ["Take Test", "Admin Panel"])

    if menu == "Admin Panel":
        pwd = st.sidebar.text_input("Enter Admin Password", type="password")
        if pwd == "admin123":
            admin_panel()
        else:
            st.error("Incorrect password!")
    else:
        mcq_test()

if __name__ == '__main__':
    main()
