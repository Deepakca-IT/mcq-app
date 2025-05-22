import streamlit as st
import pandas as pd
import os

# Load or initialize questions
@st.cache_data
def load_questions():
    return pd.read_csv("questions.csv")

def save_score(username, score, total):
    if os.path.exists("scores.csv"):
        scores = pd.read_csv("scores.csv")
    else:
        scores = pd.DataFrame(columns=["Username", "Score", "Total"])
    scores = pd.concat([scores, pd.DataFrame([{"Username": username, "Score": score, "Total": total}])], ignore_index=True)
    scores.to_csv("scores.csv", index=False)

# Admin panel
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

# Main MCQ test interface
def mcq_test():
    st.title("MCQ Test")
    username = st.text_input("Enter your name to start")

    if username:
        questions = load_questions()
        score = 0
        user_answers = []

        for i, row in questions.iterrows():
            st.subheader(f"Q{i+1}: {row['question']}")
            options = [row['option1'], row['option2'], row['option3'], row['option4']]
            user_choice = st.radio("", options, key=i)
            user_answers.append(user_choice)
            if user_choice == row['answer']:
                score += 1

        if st.button("Submit"):
            st.success(f"{username}, your score is {score}/{len(questions)}")
            save_score(username, score, len(questions))

# Entry point
def main():
    st.sidebar.title("Navigation")
    menu = st.sidebar.radio("Go to", ["Take Test", "Admin Panel"])

    if menu == "Admin Panel":
        pwd = st.sidebar.text_input("Enter Admin Password", type="password")
        if pwd == "admin123":  # Change as needed
            admin_panel()
        else:
            st.error("Incorrect password!")
    else:
        mcq_test()

if __name__ == '__main__':
    main()
