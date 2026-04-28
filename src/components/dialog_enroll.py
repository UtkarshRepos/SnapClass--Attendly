import streamlit as st
from src.database.config import supabase
from src.database.db import enroll_student_to_subject
import time


@st.dialog('Enroll in Subject')
def enroll_dialog():
    st.write("Enter the subject code provided by your teacher to enroll.")

    join_code = st.text_input("Subject Code", placeholder="e.g. MATH101-001")

    if st.button("Enroll Now", type='primary', use_container_width=True):

        if join_code:

            res = supabase.table('subjects').select('subject_id, name, subject_code').eq('subject_code', join_code).execute()

            if res.data:
                subject = res.data[0]

                student_id = st.session_state.student_data['student_id']

                check = supabase.table('subject_students').select('*').eq('subject_id', subject['subject_id']).eq('student_id', student_id).execute()

                if check.data:
                    st.warning("You are already enrolled in this subject.", icon=":material/warning:")
                else:
                    enroll_student_to_subject(subject['subject_id'], student_id)
                    st.success(f"Successfully enrolled in {subject['name']}!", icon=":material/check:")
                    time.sleep(2)
                    st.rerun()

            else:
                st.error("Invalid subject code.", icon=":material/error:")

        else:
            st.error("Please enter a valid subject code.", icon=":material/error:")