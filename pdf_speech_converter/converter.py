import os
import datetime
import pypdf
from gtts import gTTS
import pyttsx3
import speech_recognition as sr
from fpdf import FPDF

def extract_text_from_pdf(pdf_path, progress_callback=None):
    """
    Extracts text from all pages of a PDF file.
    Triggers progress_callback with strings indicating stage.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at: {pdf_path}")
        
    if progress_callback:
        progress_callback("Opening PDF file...")
        
    reader = pypdf.PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    if progress_callback:
        progress_callback(f"Found {total_pages} pages. Extracting text...")
        
    full_text = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            full_text.append(text)
        if progress_callback:
            progress_callback(f"Reading page {i + 1} of {total_pages}...")
            
    extracted_text = "\n".join(full_text).strip()
    if not extracted_text:
        raise ValueError("No text could be extracted from the PDF. It might be scanned or image-only.")
        
    return extracted_text

def text_to_speech_gtts(text, output_audio_path, lang='en', progress_callback=None):
    """
    Converts text to an MP3 file using Google Text-to-Speech (gTTS).
    """
    if progress_callback:
        progress_callback("Contacting Google TTS Engine...")
    tts = gTTS(text=text, lang=lang)
    if progress_callback:
        progress_callback("Downloading voice stream...")
    tts.save(output_audio_path)
    if progress_callback:
        progress_callback(f"AudioBook saved to: {os.path.basename(output_audio_path)}")

def text_to_speech_pyttsx3(text, output_audio_path, progress_callback=None):
    """
    Converts text to an audio file offline using pyttsx3 (SAPI5/nsss/espeak).
    """
    if progress_callback:
        progress_callback("Initializing offline TTS Engine...")
    engine = pyttsx3.init()
    
    # Configure speed and voice volume
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 0.9)
    
    if progress_callback:
        progress_callback("Synthesizing audio file offline...")
        
    engine.save_to_file(text, output_audio_path)
    engine.runAndWait()
    
    if progress_callback:
        progress_callback(f"AudioBook saved to: {os.path.basename(output_audio_path)}")

def convert_pdf_to_audiobook(pdf_path, output_audio_path, engine_type='gtts', lang='en', progress_callback=None):
    """
    Main controller to convert PDF text to audiobook.
    """
    text = extract_text_from_pdf(pdf_path, progress_callback)
    
    if engine_type == 'gtts':
        text_to_speech_gtts(text, output_audio_path, lang, progress_callback)
    else:
        text_to_speech_pyttsx3(text, output_audio_path, progress_callback)

def is_microphone_available():
    """
    Checks if PyAudio is installed and microphone input is available.
    """
    try:
        import pyaudio
        # Try listing devices to see if mic exists
        p = pyaudio.PyAudio()
        count = p.get_device_count()
        p.terminate()
        return count > 0
    except Exception:
        return False

def transcribe_audio_file(audio_path, progress_callback=None):
    """
    Transcribes an existing WAV/AIFF/FLAC audio file using Google Speech Recognition.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found at: {audio_path}")
        
    if progress_callback:
        progress_callback("Loading audio file...")
        
    r = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = r.record(source)
        
    if progress_callback:
        progress_callback("Transcribing speech (Google Web Speech API)...")
        
    try:
        text = r.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        raise Exception("Google Speech API could not understand the audio. Ensure it is clear English.")
    except sr.RequestError as e:
        raise Exception(f"Connection failed; Google Speech Service is unreachable: {e}")

def transcribe_mic_input(duration=5, progress_callback=None):
    """
    Records speech from the microphone and transcribes it.
    """
    if not is_microphone_available():
        raise RuntimeError("No microphone found or PyAudio is not installed. Please upload a WAV audio file instead.")
        
    r = sr.Recognizer()
    with sr.Microphone() as source:
        if progress_callback:
            progress_callback("Calibrating background noise... Please stay quiet.")
        r.adjust_for_ambient_noise(source, duration=1.2)
        
        if progress_callback:
            progress_callback(f"Listening... Speak now (recording for up to {duration} seconds)...")
            
        try:
            audio_data = r.listen(source, timeout=5, phrase_time_limit=duration)
        except sr.WaitTimeoutError:
            raise Exception("No speech was detected within the timeout period.")
            
    if progress_callback:
        progress_callback("Speech captured. Processing transcription...")
        
    try:
        text = r.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        raise Exception("Google Speech API could not understand the captured speech.")
    except sr.RequestError as e:
        raise Exception(f"Google Speech API request error: {e}")

def save_text_to_pdf(text, output_pdf_path, title="Transcribed Speech Document", progress_callback=None):
    """
    Compiles text string into a formatted PDF using fpdf2.
    """
    if progress_callback:
        progress_callback("Generating PDF document...")
        
    pdf = FPDF()
    pdf.add_page()
    
    # Set standard margins (15mm)
    pdf.set_margins(15, 20, 15)
    
    # Header Title
    pdf.set_font("helvetica", style="B", size=16)
    pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(8)
    
    # Subtitle with Date
    pdf.set_font("helvetica", style="I", size=10)
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    pdf.cell(0, 6, f"Generated on: {current_time}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(4)
    
    # Draw horizontal divider line
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(10)
    
    # Body Text
    pdf.set_font("helvetica", size=11)
    
    # Clean string to prevent encoding crashes (replace non-latin-1 characters safely)
    safe_text = text.encode('latin-1', 'replace').decode('latin-1')
    
    # multi_cell automatically wraps lines
    pdf.multi_cell(0, 6, safe_text)
    
    pdf.output(output_pdf_path)
    
    if progress_callback:
        progress_callback(f"PDF saved successfully to: {os.path.basename(output_pdf_path)}")
