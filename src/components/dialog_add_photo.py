import streamlit as st
from src.database.config import supabase
from src.database.db import enroll_student_to_subject
import time
from PIL import Image


@st.dialog('Capture or upload Photo')
def add_photos_dialog():
    st.write('Add classroom photos to scan for attendance')

    # ✅ FIX 1: initialize session list safely
    if "attendance_images" not in st.session_state:
        st.session_state.attendance_images = []

    if 'photo_tab' not in st.session_state:
        st.session_state.photo_tab = 'camera'

    t1, t2 = st.columns(2)

    with t1:
        type_camera = "primary" if st.session_state.photo_tab == 'camera' else 'tertiary'
        if st.button('Camera', type=type_camera, use_container_width=True):
            st.session_state.photo_tab = 'camera'

    with t2:
        type_upload = "primary" if st.session_state.photo_tab == 'upload' else 'tertiary'
        if st.button('Upload photos', type=type_upload, use_container_width=True):
            st.session_state.photo_tab = 'upload'

    # ---------------- CAMERA ----------------
    if st.session_state.photo_tab == 'camera':
        cam_photo = st.camera_input('Take Snapshot', key='dialog_cam')

        if cam_photo:
            st.session_state.attendance_images.append(Image.open(cam_photo))
            st.toast('Photo Captured')
            st.rerun()

    # ---------------- UPLOAD ----------------
    if st.session_state.photo_tab == 'upload':
        uploaded_files = st.file_uploader(
            'choose image files',
            type=['jpg', 'png', 'jpeg'],
            accept_multiple_files=True,
            key='dialog_upload'
        )

        if uploaded_files:
            for f in uploaded_files:
                st.session_state.attendance_images.append(Image.open(f))

            st.toast('Photo Uploaded Successfully')
            st.rerun()

    st.divider()

    if st.button('Done', type='primary', use_container_width=True):
        st.rerun()