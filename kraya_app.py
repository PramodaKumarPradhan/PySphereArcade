import streamlit as st
import streamlit.components.v1 as components

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

# Embed the deployed GitHub Pages URL of Kraya
# Height is set to cover the screen viewport, with scrolling enabled
components.iframe("https://pramodakumarpradhan.github.io/PySphereArcade/kraya/index.html", height=900, scrolling=True)
