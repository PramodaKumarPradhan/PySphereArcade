import os
import streamlit as st
import streamlit.components.v1 as components

# 1. Set Streamlit Page Configurations
st.set_page_config(
    page_title="GestureLink AI - Neural Hand Gesture & Robotics Simulator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit brandings and padding for a clean full-screen feel
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .block-container {
                padding-top: 1.5rem;
                padding-bottom: 0rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }
            iframe {
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# 2. Resolve Path & Load Dashboard HTML content
dashboard_path = os.path.join(
    os.path.dirname(__file__), 
    "gesture_control_system", 
    "templates", 
    "streamlit_dashboard.html"
)

html_content = ""
if os.path.exists(dashboard_path):
    with open(dashboard_path, "r", encoding="utf-8") as f:
        html_content = f.read()
else:
    st.error("Error: Could not locate the dashboard HTML template in your gesture_control_system/templates directory.")

# 3. Serve the self-contained dashboard via a custom iframe allowing camera permissions
if html_content:
    import base64
    encoded_html = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
    iframe_src = f"data:text/html;base64,{encoded_html}"
    
    iframe_html = f'''
        <iframe 
            src="{iframe_src}" 
            width="100%" 
            height="950" 
            style="border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; background-color: #060813;" 
            allow="camera; microphone; display-capture;" 
            sandbox="allow-scripts allow-same-origin allow-forms allow-popups">
        </iframe>
    '''
    st.html(iframe_html)

