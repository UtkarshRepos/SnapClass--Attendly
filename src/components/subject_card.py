import streamlit as st
from textwrap import dedent


def subject_card(name, code, section, stats=False, footer_callback=None):

    html = f"""
        <div style="background:white; border-left:8px solid #EB459E; border-radius:20px;border:1px solid black; padding:25px; margin-bottom:20px;">

            <h3 style="margin-top: 0; color: #1e293b; font-size: 1.5em;">{name}</h3>

            <p style="margin:10px 0; color: #64748b;">
                <span style="background:#E0E3FF; color:#5865F2; padding:2px 8px; border-radius:5px;">Code:</span> 
                {code} | 
                <span style="font-weight: bold;">Section:</span> {section}
            </p>
        """

    if stats:
        html += """
        <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:15px;">
        """

        for icon, label, value in stats:
            html += f"""
            <div style="background:#EB459E1A; padding:5px 12px; border-radius:1px; font-size:0.9rem;">
                <span style="background:#F0F4FF; color:#5865F2; padding:5px 10px; border-radius:5px;">{icon}</span>
                <span style="color:#64748b;">{label}: <strong>{value}</strong></span>
            </div>
            """

        html += "</div>"

    html += "</div>"

    clean_html = "\n".join(line.lstrip() for line in dedent(html).splitlines()).strip()
    st.markdown(clean_html, unsafe_allow_html=True)

    if footer_callback:
        footer_callback()