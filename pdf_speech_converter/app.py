import os
import io
import streamlit as st
import pypdf
from gtts import gTTS
import speech_recognition as sr
from fpdf import FPDF

# Import our core utility module
import converter

# Page configuration
st.set_page_config(
    page_title="Nexus PDF & Speech Web Converter",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark Cyber Aesthetic)
st.markdown("""
<style>
    .main {
        background-color: #0a0c10;
        color: #ffffff;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #121625;
        border: 1px solid #232d4b;
        border-radius: 8px 8px 0px 0px;
        padding: 8px 16px;
        color: #a0a5c0;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0066ff !important;
        color: #ffffff !important;
        border-color: #0066ff !important;
    }
    h1, h2, h3 {
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    .status-text {
        font-family: monospace;
        background-color: #0d101d;
        padding: 10px;
        border-radius: 6px;
        border: 1px solid #232d4b;
        color: #00ff88;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar branding
st.sidebar.title("🎙️ Nexus Web Converter")
st.sidebar.markdown("---")
st.sidebar.info("""
**Dual Utilities**:
1. **PDF to AudioBook**: Extract text and compile it to an audio stream.
2. **Speech to PDF**: Record voice or upload WAV file to generate PDFs.
""")
st.sidebar.markdown("---")
st.sidebar.caption("Powered by Python, Streamlit, and Google Speech APIs.")

# Main title
st.title("Nexus PDF & Speech Web Converter")
st.caption("Access global PDF audiobook creation and speech-to-PDF transcription via web browser.")

# Tabs
tab1, tab2 = st.tabs(["📖 PDF to AudioBook", "🎙️ Speech to PDF"])

# ───────────────────────────────────────────────────────────────────
# TAB 1: PDF to AudioBook
# ───────────────────────────────────────────────────────────────────
with tab1:
    st.header("PDF to AudioBook Converter")
    st.write("Upload a PDF document, extract its text, and render it to a downloadable audio file.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        uploaded_pdf = st.file_uploader("Upload PDF File", type=["pdf"])
        
        # Options
        tts_engine = st.selectbox(
            "Select TTS Engine", 
            ["gTTS (Google Online - Recommended)", "pyttsx3 (System Offline)"],
            index=0
        )
        
        lang = st.selectbox(
            "Speech Language (gTTS only)",
            ["en", "es", "fr", "de", "it", "hi"],
            index=0
        )
        
        convert_btn = st.button("Generate AudioBook", type="primary")
        
    with col2:
        st.subheader("Synthesis Output & Player")
        if uploaded_pdf is not None and convert_btn:
            try:
                with st.spinner("Processing PDF and Synthesizing Voice..."):
                    # Extract Text
                    reader = pypdf.PdfReader(uploaded_pdf)
                    text_list = []
                    total_pages = len(reader.pages)
                    
                    st.text(f"Extracting text from {total_pages} pages...")
                    for i, page in enumerate(reader.pages):
                        t = page.extract_text()
                        if t:
                            text_list.append(t)
                    
                    full_text = "\n".join(text_list).strip()
                    
                    if not full_text:
                        st.error("Could not extract any text. The PDF might be scanned or blank.")
                    else:
                        st.success(f"Successfully extracted {len(full_text)} characters of text.")
                        
                        # Generate Audio
                        st.text("Synthesizing audio file...")
                        
                        temp_audio_file = "temp_audiobook.mp3" if "gTTS" in tts_engine else "temp_audiobook.wav"
                        
                        if "gTTS" in tts_engine:
                            tts = gTTS(text=full_text, lang=lang)
                            tts.save(temp_audio_file)
                        else:
                            # Offline engine
                            engine = pyttsx3.init()
                            engine.setProperty('rate', 150)
                            engine.save_to_file(full_text, temp_audio_file)
                            engine.runAndWait()
                            
                        # Read audio bytes for player
                        with open(temp_audio_file, "rb") as f:
                            audio_bytes = f.read()
                            
                        # Remove temp file
                        if os.path.exists(temp_audio_file):
                            os.remove(temp_audio_file)
                            
                        st.success("Audio synthesis completed!")
                        
                        # Audio Player
                        st.audio(audio_bytes, format="audio/mp3" if "gTTS" in tts_engine else "audio/wav")
                        
                        # Download Button
                        st.download_button(
                            label="Download AudioBook",
                            data=audio_bytes,
                            file_name="audiobook.mp3" if "gTTS" in tts_engine else "audiobook.wav",
                            mime="audio/mp3" if "gTTS" in tts_engine else "audio/wav"
                        )
            except Exception as e:
                st.error(f"Error during conversion: {e}")
        elif convert_btn:
            st.warning("Please upload a PDF file first.")

# ───────────────────────────────────────────────────────────────────
# TAB 2: Speech to PDF
# ───────────────────────────────────────────────────────────────────
with tab2:
    st.header("Speech to PDF Converter")
    st.write("Record voice directly in your web browser or upload a WAV recording to compile a PDF.")
    
    col_input, col_output = st.columns([1, 1])
    
    with col_input:
        st.subheader("1. Audio Source")
        
        # Streamlit 1.34+ audio input widget
        has_recorded = False
        recorded_audio = None
        
        # We try to use audio_input if available in this streamlit version
        if hasattr(st, "audio_input"):
            recorded_audio = st.audio_input("Record Speech (Click microphone to start/stop)")
            if recorded_audio is not None:
                has_recorded = True
                st.success("Voice successfully captured!")
        
        st.write("**Or upload a WAV recording file:**")
        uploaded_wav = st.file_uploader("Upload WAV File", type=["wav"])
        
        transcribe_btn = st.button("Transcribe Audio", type="primary")
        
        # Perform transcription
        transcription_text = ""
        
        if transcribe_btn:
            audio_source = None
            if has_recorded and recorded_audio is not None:
                audio_source = recorded_audio
            elif uploaded_wav is not None:
                audio_source = uploaded_wav
                
            if audio_source is not None:
                try:
                    with st.spinner("Processing speech transcription..."):
                        r = sr.Recognizer()
                        # read bytes and convert to AudioFile
                        with sr.AudioFile(audio_source) as source:
                            audio_data = r.record(source)
                        
                        transcription_text = r.recognize_google(audio_data)
                        st.success("Audio transcribed successfully!")
                except Exception as e:
                    st.error(f"Transcription Error: {e}")
            else:
                st.warning("Please record your microphone input or upload a WAV audio file first.")
                
    with col_output:
        st.subheader("2. Review & Compile PDF")
        
        # User reviews/edits transcription text
        edited_text = st.text_area(
            "Review / Edit Transcribed Text:", 
            value=transcription_text if transcription_text else st.session_state.get("transcribed_value", ""),
            height=180
        )
        # Store in session state
        st.session_state["transcribed_value"] = edited_text
        
        doc_title = st.text_input("Document Title", value="Transcribed Speech Document")
        
        generate_pdf_btn = st.button("Generate PDF")
        
        if generate_pdf_btn:
            if not edited_text.strip():
                st.error("No transcription text available to generate PDF.")
            else:
                try:
                    with st.spinner("Creating PDF..."):
                        # Format PDF in memory
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_margins(15, 20, 15)
                        
                        # Title
                        pdf.set_font("helvetica", style="B", size=16)
                        pdf.cell(0, 10, doc_title, new_x="LMARGIN", new_y="NEXT", align="C")
                        pdf.ln(8)
                        
                        # Subtitle
                        pdf.set_font("helvetica", style="I", size=10)
                        import datetime
                        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        pdf.cell(0, 6, f"Generated on: {current_time} (Nexus Web App)", new_x="LMARGIN", new_y="NEXT", align="C")
                        pdf.ln(4)
                        
                        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
                        pdf.ln(10)
                        
                        # Body
                        pdf.set_font("helvetica", size=11)
                        # Clean to latin-1
                        clean_body = edited_text.encode('latin-1', 'replace').decode('latin-1')
                        pdf.multi_cell(0, 6, clean_body)
                        
                        # Output PDF stream to bytes
                        # In fpdf2, pdf.output() without arguments returns bytes, or we can write to temp and read
                        pdf_bytes = pdf.output()
                        
                        st.success("PDF generated successfully!")
                        
                        # Download Button
                        st.download_button(
                            label="Download PDF Document",
                            data=pdf_bytes,
                            file_name="speech_document.pdf",
                            mime="application/pdf"
                        )
                except Exception as e:
                    st.error(f"Failed to generate PDF: {e}")
