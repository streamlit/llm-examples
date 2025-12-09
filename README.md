import streamlit as st
import pandas as pd

# Initialize empty dataframes
students = pd.DataFrame(columns=['ID', 'Name', 'Class'])
teachers = pd.DataFrame(columns=['ID', 'Name', 'Subject'])
messages = pd.DataFrame(columns=['ID', 'Sender', 'Message'])

def main():
    st.title("JPSP School Management System")
    
menu = ["Home", "Students", "Teachers", "Messages"]
    choice = st.sidebar.selectbox("Menu", menu)
    
if choice == "Home":
        st.subheader("Home")
        st.write("Welcome to the JPSP School Management System!")
    
 elif choice == "Students":
        st.subheader("Students")
        st.dataframe(students)
        st.write("Add a new student:")
        new_id = st.text_input("ID")
        new_name = st.text_input("Name")
        new_class = st.text_input("Class")
        if st.button("Add Student"):
            students.loc[len(students)] = [new_id, new_name, new_class]
            st.success(f"Added student {new_name}")
    
elif choice == "Teachers":
        st.subheader("Teachers")
        st.dataframe(teachers)
        st.write("Add a new teacher:")
        new_id = st.text_input("ID")
        new_name = st.text_input("Name")
        new_subject = st.text_input("Subject")
        if st.button("Add Teacher"):
            teachers.loc[len(teachers)] = [new_id, new_name, new_subject]
            st.success(f"Added teacher {new_name}")
    
elif choice == "Messages":
        st.subheader("Messages")
        st.dataframe(messages)
        st.write("Add a new message:")
        new_id = st.text_input("ID")
        new_sender = st.text_input("Sender")
        new_message = st.text_area("Message")
        if st.button("Add Message"):
            messages.loc[len(messages)] = [new_id, new_sender, new_message]
            st.success(f"Added message from {new_sender}")

if __name__ == "__main__":
    main()
