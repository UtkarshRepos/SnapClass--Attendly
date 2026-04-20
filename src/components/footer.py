import streamlit as st
import base64

def footer_home():
    with open("src/images/logo.png", "rb") as f:
        img = base64.b64encode(f.read()).decode()

    st.markdown(f"""
        <div style="display:flex; justify-content:center; align-items:center; gap:10px; margin-top:2rem;">
            <p style="font-weight:bold; color:white;">Created with ❤️ by</p>
            <img src="data:image/png;base64,{img}" style="height: 42px;margin-top: -12px;margin-left: -10px;" />
        </div>
    """, unsafe_allow_html=True)