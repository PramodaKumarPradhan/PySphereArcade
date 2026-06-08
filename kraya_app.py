import streamlit as st
import streamlit.components.v1 as components
import os

# Configure Streamlit page options
st.set_page_config(
    page_title="Kraya | Online Shopping Site",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to hide Streamlit header, footer, and default margins for a white-label premium feel
hide_streamlit_branding = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        padding-left: 0rem;
        padding-right: 0rem;
    }
    iframe {
        border: none;
        width: 100%;
        height: 100vh;
    }
    </style>
"""
st.markdown(hide_streamlit_branding, unsafe_allow_html=True)

# Load the self-contained Kraya HTML package
base_dir = os.path.dirname(os.path.abspath(__file__))
html_path = os.path.join(base_dir, 'kraya', 'index_streamlit.html')

if os.path.exists(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    # Render self-contained e-commerce site directly
    components.html(html_content, height=950, scrolling=True)
else:
    st.error("Kraya application package is missing! Please run 'build_bundle.py' first.")
