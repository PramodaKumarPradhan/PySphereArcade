import streamlit as st
import os
import sys
import datetime

# Add current directory to path to allow importing language modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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

# ── USER INPUT & PROCESSING ────────────────────────────────────────────────
if user_query := st.chat_input("Tulis sesuatu... / Speak or type a command..."):
    # Display user query
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})

    # 1. Detect input language
    detected_lang = translator.detect_language(user_query)
    
    # 2. Translate query to English for processing
    normalized_query = user_query.strip().lower()
    if detected_lang == 'hi':
        normalized_query = translator.hindi_to_english_command(user_query)
    elif detected_lang == 'ms':
        normalized_query = translator.translate(user_query, src='ms', dest='en')

    # 3. Formulate the response
    response_en = ""
    action_taken = ""

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
        # Check if Gemini key is available in environment
        gemini_key = os.environ.get("GEMINI_API_KEY", "")
        if gemini_key:
            try:
                import google.genai as genai
                client = genai.Client(api_key=gemini_key)
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=user_query,
                )
                response_en = response.text
            except Exception as e:
                response_en = f"I'm not sure how to handle that. (Error calling cloud AI: {e})"
        else:
            response_en = "I received your command. In local mode, I would execute this on your laptop!"

    # 4. Translate response back to user's language
    final_response = translator.get_response_in_language(response_en, detected_lang)

    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(final_response)
    st.session_state.messages.append({"role": "assistant", "content": final_response})
