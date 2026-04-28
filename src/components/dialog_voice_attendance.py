import streamlit as st
from src.pipeline.voice_pipeline import process_bulk_audio
from src.database.config import supabase
from datetime import datetime
import pandas as pd
from src.components.dialog_attendance_result import show_attendance_results


@st.dialog('Voice Attendance')
def voice_attendance_dialog(selected_subject_id):
    st.write('Record audio saying I am present. Then AI will recognize the student')

    audio_data = st.audio_input("Record classroom audio")

    if st.button('Analyze Audio', use_container_width=True, type='primary'):

        if not audio_data:
            st.error("Please record audio first")
            return

        with st.spinner('Processing Audio data'):

            # ✅ FIX 1: consistent join name
            enrolled_res = supabase.table('subject_students') \
                .select("*,student(*)") \
                .eq('subject_id', selected_subject_id) \
                .execute()

            enrolled_students = enrolled_res.data

            if not enrolled_students:
                st.warning('No student enrolled in this course')
                return

            # ✅ FIX 2: correct key + safe access
            candidates_dict = {
                s['student']['student_id']: s['student']['voice_embedding']
                for s in enrolled_students
                if s.get('student') and s['student'].get('voice_embedding')
            }

            if not candidates_dict:
                st.error('No enrolled students have voice profiles registered')
                return

            audio_bytes = audio_data.read()

            # ✅ FIX 3: typo corrected
            detected_scores = process_bulk_audio(audio_bytes, candidates_dict)

            results, attendance_to_log = [], []

            current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            for node in enrolled_students:

                # ❌ FIX 4: remove comma (VERY IMPORTANT)
                student = node['student']

                score = detected_scores.get(student['student_id'], 0.0)
                is_present = bool(score > 0)

                results.append({
                    "Name": student['name'],
                    "ID": student['student_id'],
                    "Source": score if is_present else "-",
                    "Status": "✅ Present" if is_present else "❌ Absent"
                })

                attendance_to_log.append({
                    'student_id': student['student_id'],
                    'subject_id': selected_subject_id,
                    'timestamp': current_timestamp,
                    'is_present': is_present
                })

            st.session_state.voice_attendance_results = (
                pd.DataFrame(results),
                attendance_to_log
            )

    if st.session_state.get('voice_attendance_results'):
        st.divider()
        df_results, logs = st.session_state.voice_attendance_results
        show_attendance_results(df_results, logs)