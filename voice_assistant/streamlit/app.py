import streamlit as st
import os
import sys
import datetime

# Add the parent directory to path to allow importing language modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from language.translator import LanguageTranslator

# ── STREAMLIT PAGE SETUP ──────────────────────────────────────────────────
st.set_page_config(
    page_title="ARIA — Multilingual Voice Assistant",
    page_icon="🎙️",
    layout="centered"
)

# Initialize Session State for Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Selamat Datang! I'm ARIA, your multilingual voice assistant. I support English, Hindi, and Malay. How can I help you today?"}
    ]

# Load default config
config = {
    "language": {
        "default": "en",
        "available": ["en", "hi", "ms"],
        "recognition_locale_en": "en-IN",
        "recognition_locale_hi": "hi-IN",
        "recognition_locale_ms": "ms-MY",
        "auto_detect": True
    }
}
translator = LanguageTranslator(config)

# ── SIDEBAR DEBUG PANEL ──────────────────────────────────────────────────
st.sidebar.title("🛠️ System Debugger")

# Check secrets
has_secret = False
secret_keys = []
secrets_error = None

try:
    if st.secrets:
        secret_keys = list(st.secrets.keys())
        if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"].strip():
            has_secret = True
except Exception as e:
    secrets_error = str(e)

# Check environment variables
has_env = "GEMINI_API_KEY" in os.environ and os.environ["GEMINI_API_KEY"].strip()

# Status Display
if has_secret:
    st.sidebar.success("🔑 API Key: Found in Secrets!")
elif has_env:
    st.sidebar.success("🔑 API Key: Found in Environment!")
else:
    st.sidebar.error("❌ API Key: Not Found")
    st.sidebar.warning(
        "Please check your Streamlit Secrets. Ensure you wrote it exactly as: \n"
        '`GEMINI_API_KEY = "your_key_here"`'
    )

# List found keys (safe)
if secret_keys:
    st.sidebar.write("Available Secret Keys:", secret_keys)
if secrets_error:
    st.sidebar.write("Secrets Error:", secrets_error)

# ── HEADER ───────────────────────────────────────────────────────────────
st.title("🎙️ ARIA — Conversational Assistant")
st.caption("Multilingual Demo (English + Hindi + Malay) running in the Cloud")

# Inform the user about cloud execution limitations
st.info(
    "💡 **Cloud Demo Info:** System controls (volume, brightness, launching local apps) are simulated "
    "here because the app is running in the cloud. For full system automation, run ARIA locally using `run.bat`."
)

# ── CHAT HISTORY DISPLAY ──────────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── USER INPUT FORM (INLINE) ──────────────────────────────────────────────
# We use st.form instead of st.chat_input because some corporate web browsers 
# block absolute-positioned overlays at the bottom of the page.
with st.form("chat_form", clear_on_submit=True):
    user_query = st.text_input(
        "Speak or type a command...",
        placeholder="Tulis sesuatu... / Type a command here...",
        label_visibility="collapsed"
    )
    submit_button = st.form_submit_button("Send Command 🚀")

if submit_button and user_query.strip():
    # Append user message to history
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Rerun the message display to show user's text immediately
    st.rerun()

# ── PROCESS LAST MESSAGE IF FROM USER ─────────────────────────────────────
# This pattern ensures the processing occurs on rerun and registers correctly.
if st.session_state.messages[-1]["role"] == "user":
    last_query = st.session_state.messages[-1]["content"]
    
    with st.spinner("Thinking..."):
        # 1. Detect input language
        detected_lang = translator.detect_language(last_query)
        
        # 2. Translate query to English for processing
        normalized_query = last_query.strip().lower()
        if detected_lang == 'hi':
            normalized_query = translator.hindi_to_english_command(last_query)
        elif detected_lang == 'ms':
            normalized_query = translator.translate(last_query, src='ms', dest='en')

        # 3. Formulate the response
        response_en = ""

        # Rule-based routing simulation
        if any(w in normalized_query for w in ["hello", "hi", "hey", "apa khabar", "namaste"]):
            response_en = "Hello! Hope you are doing great. How can I assist you?"
        elif "time" in normalized_query:
            now = datetime.datetime.now().strftime("%I:%M %p")
            response_en = f"The current time is {now}."
        elif "date" in normalized_query:
            today = datetime.datetime.now().strftime("%A, %d %B %Y")
            response_en = f"Today is {today}."
        elif "notepad" in normalized_query:
            response_en = "Opening Notepad... (Simulated: Notepad command received in the cloud)."
        elif "volume" in normalized_query or "mute" in normalized_query:
            response_en = "Adjusting volume... (Simulated: Audio command received in the cloud)."
        elif "screenshot" in normalized_query:
            response_en = "Taking screenshot... (Simulated: Capture command received in the cloud)."
        else:
            # Get Gemini key
            gemini_key = ""
            if has_secret:
                gemini_key = st.secrets["GEMINI_API_KEY"]
            elif has_env:
                gemini_key = os.environ["GEMINI_API_KEY"]

            if gemini_key:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=gemini_key)
                    
                    response_text = None
                    last_error = None
                    
                    # Try multiple model variants to bypass regional/key restrictions
                    for model_name in ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-pro"]:
                        try:
                            model = genai.GenerativeModel(model_name)
                            response = model.generate_content(last_query)
                            response_text = response.text
                            break
                        except Exception as inner_e:
                            last_error = inner_e
                            continue
                            
                    if response_text:
                        response_en = response_text
                    else:
                        raise last_error
                except Exception as e:
                    response_en = f"I'm not sure how to handle that. (Error calling cloud AI: {e})"
            else:
                response_en = "I received your command. In local mode, I would execute this on your laptop!"

        # 4. Translate response back to user's language
        final_response = translator.get_response_in_language(response_en, detected_lang)

        # Append assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": final_response})
        
        # Rerun to show assistant response
        st.rerun()
