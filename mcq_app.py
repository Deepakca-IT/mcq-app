import streamlit as st
import pandas as pd
import os
import random

@st.cache_data def load_questions(): return pd.read_csv("questions.csv")

def save_score(username, score, total): if os.path.exists("scores.csv"): scores = pd.read_csv("scores.csv") else: scores = pd.DataFrame(columns=["Username", "Score", "Total"]) scores = pd.concat([scores, pd.DataFrame([{"Username": username, "Score": score, "Total": total}])], ignore_index=True) scores.to_csv("scores.csv", index=False)

def admin_panel(): st.title("Admin Panel")

uploaded_file = st.file_uploader("Upload CSV to add questions", type=["csv"])
if uploaded_file is not None:
    df_new = pd.read_csv(uploaded_file)
    df_old = load_questions()
    df_combined = pd.concat([df_old, df_new], ignore_index=True)
    df_combined.to_csv("questions.csv", index=False)
    st.success("Questions updated successfully!")

st.write("Current Questions:")
st.dataframe(load_questions())

def mcq_test(): st.title("MCQ Test") username = st.text_input("Enter your name to start")

if username:
    if "questions_order" not in st.session_state:
        questions = load_questions()
        st.session_state.questions_order = random.sample(range(len(questions)), len(questions))
        st.session_state.current_index = 0
        st.session_state.score = 0
        st.session_state.user_answers = []
        st.session_state.show_feedback = False

    questions = load_questions()
    index = st.session_state.questions_order[st.session_state.current_index]
    row = questions.iloc[index]

    st.subheader(f"Q{st.session_state.current_index + 1}: {row['question']}")
    options = [row['option1'], row['option2'], row['option3'], row['option4']]

    if "selected_option" not in st.session_state:
        st.session_state.selected_option = None

    for option in options:
        if st.session_state.selected_option:
            if option == row['answer']:
                st.markdown(f"<div style='color: green; font-weight: bold'>{option}</div>", unsafe_allow_html=True)
            elif option == st.session_state.selected_option:
                st.markdown(f"<div style='color: red; font-weight: bold'>{option}</div>", unsafe_allow_html=True)
            else:
                st.markdown(option)
        else:
            if st.button(option):
                st.session_state.selected_option = option
                if option == row['answer']:
                    st.session_state.score += 1

    if st.session_state.selected_option:
        if st.button("Next"):
            st.session_state.user_answers.append(st.session_state.selected_option)
            st.session_state.current_index += 1
            st.session_state.selected_option = None
            if st.session_state.current_index >= len(st.session_state.questions_order):
                st.success(f"{username}, your score is {st.session_state.score}/{len(st.session_state.questions_order)}")
                save_score(username, st.session_state.score, len(st.session_state.questions_order))
                st.session_state.clear()

def main(): st.sidebar.title("Navigation") menu = st.sidebar.radio("Go to", ["Take Test", "Admin Panel"])

if menu == "Admin Panel":
    pwd = st.sidebar.text_input("Enter Admin Password", type="password")
    if pwd == "admin123":
        admin_panel()
    else:
        st.error("Incorrect password!")
else:
    mcq_test()

if name == 'main': main()

