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

# Show standard Streamlit UI for debugging errors
st.title("GestureLink AI - Touchless Robotics Dashboard")
st.write("Initializing WebAssembly vision engine inside your browser...")


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

# 3. Serve the self-contained dashboard via components.html
if html_content:
    components.html(html_content, height=950, scrolling=True)


