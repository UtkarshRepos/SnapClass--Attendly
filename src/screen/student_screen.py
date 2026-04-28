import streamlit as st
import supabase

from src.pipeline.face_pipeline import predict_attendance , get_face_embedding, train_classifier
from src.pipeline.voice_pipeline import get_voice_embedding
from src.database.db import create_student , get_all_students, get_student_subjects, get_student_attendance, unenroll_student_to_subject
from src.components.footer import footer_dashboard
from src.components.header import header_dashboard
from src.ui.base_layout import style_background_dashboard , style_base_layout
from PIL import Image
import numpy as np
import time

from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card



def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data['student_id']
    c1,c2  = st.columns(2, vertical_alignment='center', gap='xxlarge')

    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"""Welcome, {student_data['name']}!""", text_alignment='center')
        if st.button('Logout', type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['is_logged_in'] = False
            del st.session_state.student_data
            st.rerun()
    
    st.space()


    c1,c2 = st.columns(2)
    with c1:
        st.header('Your Enrolled Subjects')
    with c2:
        if st.button('Enroll in Subject', type='primary', width='stretch', icon=':material/add:'):
            enroll_dialog()

    st.divider()

    with st.spinner('Loading Your Enrll Subject...'):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)
        


    
    stats_map = {}

    for log in logs:
        sid = log['subject_id']

        if sid not in stats_map:
            stats_map[sid] = {"total": 0, "attended": 0}

        stats_map[sid]["total"] += 1

        if log.get("is_present"):
            stats_map[sid]["attended"] += 1

    if subjects:
        cols = st.columns(2)
        for i, sub_node in enumerate(subjects):
            sub = sub_node["subjects"]
            sid = sub["subject_id"]

            stats = stats_map.get(sid, {"total": 0, "attended": 0})

            def unenroll_btn(subject_id=sid, subject_name=sub["name"]):
                if st.button(
                    "Unenroll from this course",
                    type="tertiary",
                    width="stretch",
                    icon=":material/delete_forever:",
                    key=f"unenroll_{subject_id}",
                ):
                    unenroll_student_to_subject(subject_id, student_id)
                    st.toast(f"Unenrolled from {subject_name} successfully!")
                    st.rerun()

            with cols[i % 2]:
                subject_card(
                    name=sub["name"],
                    code=sub["subject_code"],
                    section=sub["section"],
                    stats=[
                        ("📅", "Total", stats["total"]),
                        ("✅", "Attended", stats["attended"]),
                    ],
                    footer_callback=unenroll_btn,
                )
    else:
        st.info("No enrolled subjects yet. Use 'Enroll in Subject' to join one.")

    footer_dashboard()



    
def student_screen():

    style_background_dashboard()
    style_base_layout()

    if "student_data" in st.session_state:
        student_dashboard()
        return
    c1,c2  = st.columns(2, vertical_alignment='center', gap='xxlarge')

    with c1:
        header_dashboard()
    with c2:
        if st.button('Go to Home', type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

        # header_dashboard()
    st.header('Login using Face ID', text_alignment='center')
    st.space()
    st.space()


    show_registration = False

    
    photo_source = st.camera_input("Position your face in the center")

    if photo_source:
        img = np.array(Image.open(photo_source))

        with st.spinner('AI is scanning...'):
            detected, all_ids, num_faces = predict_attendance(img)


            if num_faces == 0:
                st.error('No face detected. Please try again.')
            elif num_faces > 1:
                st.error('Multiple faces detected. Please ensure only your face is visible and try again.')
            else:
                if detected:
                    student_id = list(detected.keys())[0]
                    all_students = get_all_students()
                    student = next((s for s in all_students if s['student_id'] == student_id), None)
                    

                    if student:
                        st.session_state.is_logged_in = True
                        st.session_state.user_role = 'student'
                        st.session_state.student_data = student
                        st.toast(f"Welcome, {student['name']}!", icon='👋', duration=3000)
                        time.sleep(1)
                        st.rerun()  
                else:
                    st.error('Face not recognized! You might be a new student!')
                    show_registration = True
            # Simulate processing time

    if show_registration:
        with st.container(border= True):
            st.header('Register new Profile')
            new_name = st.text_input('Enter your name', placeholder='Your Name')

            st.subheader('Optional: Voice Enrollment')
            st.info("Enroll yur for voice attendance ")

            audio_data = None

            try:
                audio_data = st.audio_input("Record your short pharase like Iam present, My name is John etc")
            except Exception:
                st.error('Audio Data failed to capture. Please try again.')
            
            if st.button('Create Account', type='primary'):
                if new_name:
                    with st.spinner('Creating profile...'):
                        # Here you would typically save the new student data to your database
                        img = np.array(Image.open(photo_source))
                        encoding = get_face_embedding(img)
                        if encoding:
                            face_emb= encoding[0].tolist()

                            voice_emb = None
                            if audio_data:
                                voice_emb = get_voice_embedding(audio_data.read())
                            
                            response_data = create_student(new_name, face_emb, voice_emb)
                            if response_data:
                                train_classifier()

                                st.session_state.is_logged_in = True
                                st.session_state.user_role = 'student'
                                st.session_state.student_data = response_data[0]
                                st.toast(f"Welcome, {new_name}! Your profile has been created.", icon='👋', duration=3000)
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error('Could not capture your facial feature for registration.')
                else:
                    st.warning('Please enter your name to create an account.')


    footer_dashboard()


