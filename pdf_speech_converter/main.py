import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue

# Import core converter utilities
import converter

# Color system matching the Cyber/Nexus theme
BG_DEEP = "#0a0c12"        # Dark canvas background
BG_CARD = "#121625"        # Glassmorphic card frame
BORDER_COLOR = "#232d4b"   # Neon cyber borders
PRIMARY_COLOR = "#0066ff"  # Electric blue
ACCENT_COLOR = "#8a2be2"   # Purple accent
TEXT_PRIMARY = "#ffffff"   # Bright white
TEXT_SECONDARY = "#a0a5c0" # Dim gray
SUCCESS_COLOR = "#00ff88"  # Green
WARNING_COLOR = "#ffaa00"  # Amber

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Nexus PDF & Speech Converter")
        self.geometry("960x680")
        self.configure(bg=BG_DEEP)
        
        # Thread communication queue
        self.log_queue = queue.Queue()
        
        # Configure styles
        self.setup_styles()
        
        # State variables
        self.pdf_file_path = tk.StringVar()
        self.audio_file_path = tk.StringVar()
        self.tts_engine = tk.StringVar(value="gtts")
        self.tts_lang = tk.StringVar(value="en")
        self.record_duration = tk.IntVar(value=10)
        self.audio_source = tk.StringVar(value="file") # "file" or "mic"
        self.is_mic_ready = converter.is_microphone_available()
        
        # Build UI layout
        self.build_ui()
        
        # Start queue processing
        self.process_queue()
        
    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        
        # Frame Styles
        style.configure("TFrame", background=BG_DEEP)
        style.configure("Card.TFrame", background=BG_CARD, bordercolor=BORDER_COLOR, borderwidth=1, relief="solid")
        
        # Label Styles
        style.configure("TLabel", background=BG_DEEP, foreground=TEXT_PRIMARY, font=("Inter", 10))
        style.configure("Card.TLabel", background=BG_CARD, foreground=TEXT_PRIMARY, font=("Inter", 10))
        style.configure("Header.TLabel", background=BG_CARD, foreground=TEXT_PRIMARY, font=("Inter", 12, "bold"))
        style.configure("Title.TLabel", background=BG_DEEP, foreground=TEXT_PRIMARY, font=("Inter", 18, "bold"))
        
        # Button Styles
        style.configure("TButton", background=PRIMARY_COLOR, foreground=TEXT_PRIMARY, borderwidth=0, font=("Inter", 10, "bold"), padding=6)
        style.map("TButton",
                  background=[("active", ACCENT_COLOR), ("disabled", "#3b3e4f")],
                  foreground=[("disabled", "#707280")])
                  
        style.configure("Secondary.TButton", background="#2a2e45", foreground=TEXT_PRIMARY, borderwidth=0, font=("Inter", 10), padding=6)
        style.map("Secondary.TButton", background=[("active", "#3f4569")])
        
        # Radio / Combobox styles
        style.configure("TRadiobutton", background=BG_CARD, foreground=TEXT_SECONDARY, font=("Inter", 10))
        style.map("TRadiobutton", foreground=[("selected", TEXT_PRIMARY), ("active", TEXT_PRIMARY)])
        
        style.configure("TCombobox", fieldbackground="#1b2038", background=BG_CARD, foreground=TEXT_PRIMARY, arrowcolor=TEXT_PRIMARY)
        
    def build_ui(self):
        # Top Header Brand
        brand_frame = ttk.Frame(self)
        brand_frame.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        brand_label = ttk.Label(brand_frame, text="Nexus PDF & Speech Converter Dashboard", style="Title.TLabel")
        brand_label.pack(side=tk.LEFT)
        
        mic_status = "Microphone: Available" if self.is_mic_ready else "Microphone: Missing PyAudio (Upload WAV only)"
        mic_color = SUCCESS_COLOR if self.is_mic_ready else WARNING_COLOR
        mic_label = tk.Label(brand_frame, text=mic_status, bg=BG_DEEP, fg=mic_color, font=("Inter", 9, "bold"))
        mic_label.pack(side=tk.RIGHT, pady=8)
        
        # Main Panels Splitter
        main_panes = ttk.Frame(self)
        main_panes.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        main_panes.columnconfigure(0, weight=1, uniform="equal")
        main_panes.columnconfigure(1, weight=1, uniform="equal")
        main_panes.rowconfigure(0, weight=1)
        
        # ───────────────────────────────────────────────────────────────────
        # LEFT PANEL: PDF to AudioBook
        # ───────────────────────────────────────────────────────────────────
        left_card = ttk.Frame(main_panes, style="Card.TFrame")
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Header padding
        hdr_left = ttk.Frame(left_card, style="Card.TFrame")
        hdr_left.pack(fill=tk.X, padx=15, pady=15)
        ttk.Label(hdr_left, text="📖 1. PDF to AudioBook Converter", style="Header.TLabel").pack(anchor=tk.W)
        
        # File selector block
        file_frame = ttk.Frame(left_card, style="Card.TFrame")
        file_frame.pack(fill=tk.X, padx=15, pady=10)
        
        ttk.Label(file_frame, text="Select PDF File Source:", style="Card.TLabel").pack(anchor=tk.W, pady=(0, 5))
        
        file_entry_row = ttk.Frame(file_frame, style="Card.TFrame")
        file_entry_row.pack(fill=tk.X)
        self.pdf_entry = tk.Entry(file_entry_row, textvariable=self.pdf_file_path, bg="#1a1e30", fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY, borderwidth=1, relief="solid", font=("Inter", 9))
        self.pdf_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4, padx=(0, 5))
        ttk.Button(file_entry_row, text="Browse", command=self.browse_pdf, width=8).pack(side=tk.RIGHT)
        
        # TTS Engine Options
        engine_frame = ttk.Frame(left_card, style="Card.TFrame")
        engine_frame.pack(fill=tk.X, padx=15, pady=10)
        
        ttk.Label(engine_frame, text="Text-to-Speech Engine:", style="Card.TLabel").pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(engine_frame, text="Google Cloud TTS (Natural voice online)", variable=self.tts_engine, value="gtts", command=self.toggle_lang_select).pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(engine_frame, text="System TTS Voice (Offline generator)", variable=self.tts_engine, value="pyttsx3", command=self.toggle_lang_select).pack(anchor=tk.W, pady=2)
        
        # Language Select (for gTTS)
        self.lang_frame = ttk.Frame(left_card, style="Card.TFrame")
        self.lang_frame.pack(fill=tk.X, padx=15, pady=10)
        ttk.Label(self.lang_frame, text="Speech Language:", style="Card.TLabel").pack(side=tk.LEFT, padx=(0, 10))
        self.lang_combobox = ttk.Combobox(self.lang_frame, textvariable=self.tts_lang, values=["en", "es", "fr", "de", "it", "hi"], width=6, state="readonly")
        self.lang_combobox.pack(side=tk.LEFT)
        
        # Convert Button & Logs
        action_frame_left = ttk.Frame(left_card, style="Card.TFrame")
        action_frame_left.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.btn_convert_pdf = ttk.Button(action_frame_left, text="Convert to Audiobook File", command=self.start_pdf_conversion)
        self.btn_convert_pdf.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(action_frame_left, text="Conversion Status / Progress:", style="Card.TLabel").pack(anchor=tk.W)
        self.pdf_log_text = tk.Text(action_frame_left, bg="#0d101d", fg=TEXT_SECONDARY, font=("Consolas", 9), height=8, borderwidth=1, relief="solid", insertbackground=TEXT_PRIMARY)
        self.pdf_log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.pdf_log_text.config(state="disabled")
        
        # ───────────────────────────────────────────────────────────────────
        # RIGHT PANEL: Speech to PDF
        # ───────────────────────────────────────────────────────────────────
        right_card = ttk.Frame(main_panes, style="Card.TFrame")
        right_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Header padding
        hdr_right = ttk.Frame(right_card, style="Card.TFrame")
        hdr_right.pack(fill=tk.X, padx=15, pady=15)
        ttk.Label(hdr_right, text="🎤 2. Speech to PDF Converter", style="Header.TLabel").pack(anchor=tk.W)
        
        # Source toggles
        src_frame = ttk.Frame(right_card, style="Card.TFrame")
        src_frame.pack(fill=tk.X, padx=15, pady=5)
        ttk.Label(src_frame, text="Audio Input Source Selection:", style="Card.TLabel").pack(anchor=tk.W, pady=(0, 3))
        
        source_options_frame = ttk.Frame(src_frame, style="Card.TFrame")
        source_options_frame.pack(fill=tk.X)
        ttk.Radiobutton(source_options_frame, text="Speech File (.wav)", variable=self.audio_source, value="file", command=self.toggle_audio_source).pack(side=tk.LEFT, padx=(0, 15))
        
        # Enable mic option if pyaudio installed
        self.rb_mic = ttk.Radiobutton(source_options_frame, text="Record Microphone", variable=self.audio_source, value="mic", command=self.toggle_audio_source)
        self.rb_mic.pack(side=tk.LEFT)
        if not self.is_mic_ready:
            self.rb_mic.configure(state="disabled")
            
        # Audio File Selector Row
        self.audio_file_frame = ttk.Frame(right_card, style="Card.TFrame")
        self.audio_file_frame.pack(fill=tk.X, padx=15, pady=10)
        ttk.Label(self.audio_file_frame, text="Select WAV File Source:", style="Card.TLabel").pack(anchor=tk.W, pady=(0, 5))
        
        audio_entry_row = ttk.Frame(self.audio_file_frame, style="Card.TFrame")
        audio_entry_row.pack(fill=tk.X)
        self.audio_entry = tk.Entry(audio_entry_row, textvariable=self.audio_file_path, bg="#1a1e30", fg=TEXT_PRIMARY, borderwidth=1, relief="solid", font=("Inter", 9))
        self.audio_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4, padx=(0, 5))
        ttk.Button(audio_entry_row, text="Browse", command=self.browse_audio, width=8).pack(side=tk.RIGHT)
        
        # Mic Recording Options Row
        self.mic_options_frame = ttk.Frame(right_card, style="Card.TFrame")
        # Pack this hidden initially
        
        ttk.Label(self.mic_options_frame, text="Recording Duration (Seconds):", style="Card.TLabel").pack(side=tk.LEFT, padx=(0, 10))
        self.duration_spin = tk.Spinbox(self.mic_options_frame, from_=5, to=60, increment=5, textvariable=self.record_duration, width=5, bg="#1a1e30", fg=TEXT_PRIMARY, buttonbackground=BG_CARD)
        self.duration_spin.pack(side=tk.LEFT)
        
        # Transcribe Buttons
        transcribe_frame = ttk.Frame(right_card, style="Card.TFrame")
        transcribe_frame.pack(fill=tk.X, padx=15, pady=5)
        self.btn_transcribe = ttk.Button(transcribe_frame, text="Transcribe Input Speech", command=self.start_transcription)
        self.btn_transcribe.pack(fill=tk.X)
        
        # Transcription Output Window (Editable text box)
        text_frame = ttk.Frame(right_card, style="Card.TFrame")
        text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        ttk.Label(text_frame, text="Review / Edit Transcribed Text:", style="Card.TLabel").pack(anchor=tk.W, pady=(0, 3))
        self.transcribed_text_box = tk.Text(text_frame, bg="#0d101d", fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY, font=("Inter", 9), height=6, borderwidth=1, relief="solid", wrap=tk.WORD)
        self.transcribed_text_box.pack(fill=tk.BOTH, expand=True)
        
        # PDF compilation Title & Save block
        save_frame = ttk.Frame(right_card, style="Card.TFrame")
        save_frame.pack(fill=tk.X, padx=15, pady=(5, 15))
        
        title_row = ttk.Frame(save_frame, style="Card.TFrame")
        title_row.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(title_row, text="Document Title:", style="Card.TLabel").pack(side=tk.LEFT, padx=(0, 5))
        self.doc_title_entry = tk.Entry(title_row, bg="#1a1e30", fg=TEXT_PRIMARY, borderwidth=1, relief="solid", font=("Inter", 9))
        self.doc_title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)
        self.doc_title_entry.insert(0, "Transcribed Speech Document")
        
        self.btn_save_pdf = ttk.Button(save_frame, text="Compile Text to PDF File", command=self.save_pdf_file)
        self.btn_save_pdf.pack(fill=tk.X)
        
        # Bottom Status Bar
        self.status_bar = tk.Label(self, text="Ready", bg=BG_CARD, fg=TEXT_SECONDARY, font=("Inter", 9), anchor="w", padx=15, pady=4, relief="ridge")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    # ── UI Toggle Logics ───────────────────────────────────────────────────────
    def toggle_lang_select(self):
        if self.tts_engine.get() == "gtts":
            self.lang_frame.pack(fill=tk.X, padx=15, pady=10)
        else:
            self.lang_frame.pack_forget()
            
    def toggle_audio_source(self):
        if self.audio_source.get() == "file":
            self.mic_options_frame.pack_forget()
            self.audio_file_frame.pack(fill=tk.X, padx=15, pady=10)
        else:
            self.audio_file_frame.pack_forget()
            self.mic_options_frame.pack(fill=tk.X, padx=15, pady=10)
            
    # ── Browse File Logics ──────────────────────────────────────────────────────
    def browse_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Documents", "*.pdf")])
        if path:
            self.pdf_file_path.set(path)
            
    def browse_audio(self):
        path = filedialog.askopenfilename(filetypes=[("WAV Audio Files", "*.wav")])
        if path:
            self.audio_file_path.set(path)
            
    # ── Thread Logics & Queue System ──────────────────────────────────────────
    def write_pdf_log(self, text):
        self.log_queue.put(("pdf_log", text))
        
    def set_status(self, text):
        self.log_queue.put(("status", text))
        
    def process_queue(self):
        try:
            while True:
                msg_type, content = self.log_queue.get_nowait()
                if msg_type == "pdf_log":
                    self.pdf_log_text.config(state="normal")
                    self.pdf_log_text.insert(tk.END, content + "\n")
                    self.pdf_log_text.see(tk.END)
                    self.pdf_log_text.config(state="disabled")
                elif msg_type == "status":
                    self.status_bar.config(text=content)
                self.log_queue.task_done()
        except queue.Empty:
            pass
        self.after(100, self.process_queue)
        
    # ── PDF to Audio Thread Trigger ───────────────────────────────────────────
    def start_pdf_conversion(self):
        pdf_path = self.pdf_file_path.get().strip()
        if not pdf_path:
            messagebox.showerror("Error", "Please select a PDF file source first.")
            return
            
        # Select output audiobook save path
        engine = self.tts_engine.get()
        ext = ".mp3" if engine == "gtts" else ".wav"
        output_path = filedialog.asksaveasfilename(
            defaultextension=ext,
            filetypes=[("Audio Files", f"*{ext}")],
            initialfile=os.path.splitext(os.path.basename(pdf_path))[0] + "_audiobook"
        )
        if not output_path:
            return
            
        # Disable buttons during conversion
        self.btn_convert_pdf.config(state="disabled")
        self.set_status("Processing PDF Audiobook...")
        self.pdf_log_text.config(state="normal")
        self.pdf_log_text.delete("1.0", tk.END)
        self.pdf_log_text.config(state="disabled")
        
        # Spawn background thread to prevent UI freezing
        lang = self.tts_lang.get()
        t = threading.Thread(target=self.run_pdf_conversion, args=(pdf_path, output_path, engine, lang), daemon=True)
        t.start()
        
    def run_pdf_conversion(self, pdf_path, output_path, engine, lang):
        try:
            def callback(msg):
                self.write_pdf_log(f"[*] {msg}")
                self.set_status(msg)
                
            converter.convert_pdf_to_audiobook(
                pdf_path=pdf_path,
                output_audio_path=output_path,
                engine_type=engine,
                lang=lang,
                progress_callback=callback
            )
            self.write_pdf_log("[+] Conversion completed successfully!")
            self.set_status("AudioBook conversion complete.")
            messagebox.showinfo("Success", f"AudioBook successfully saved to:\n{output_path}")
        except Exception as e:
            self.write_pdf_log(f"[ERROR] {str(e)}")
            self.set_status("AudioBook conversion failed.")
            messagebox.showerror("Conversion Failed", str(e))
        finally:
            self.btn_convert_pdf.config(state="normal")
            
    # ── Speech to Text Thread Trigger ──────────────────────────────────────────
    def start_transcription(self):
        src = self.audio_source.get()
        
        if src == "file":
            audio_path = self.audio_file_path.get().strip()
            if not audio_path:
                messagebox.showerror("Error", "Please select a WAV audio file first.")
                return
            self.set_status("Transcribing audio file...")
            self.btn_transcribe.config(state="disabled")
            t = threading.Thread(target=self.run_file_transcription, args=(audio_path,), daemon=True)
            t.start()
        else:
            if not self.is_mic_ready:
                messagebox.showerror("Error", "Microphone input is unavailable.")
                return
            duration = self.record_duration.get()
            self.set_status("Listening to microphone...")
            self.btn_transcribe.config(state="disabled")
            t = threading.Thread(target=self.run_mic_transcription, args=(duration,), daemon=True)
            t.start()
            
    def run_file_transcription(self, audio_path):
        try:
            def callback(msg):
                self.set_status(msg)
                
            text = converter.transcribe_audio_file(audio_path, progress_callback=callback)
            
            # Update textbox in main thread
            self.transcribed_text_box.delete("1.0", tk.END)
            self.transcribed_text_box.insert(tk.END, text)
            self.set_status("Transcription complete.")
            messagebox.showinfo("Success", "Audio transcription successfully loaded!")
        except Exception as e:
            self.set_status("Transcription failed.")
            messagebox.showerror("Transcription Failed", str(e))
        finally:
            self.btn_transcribe.config(state="normal")
            
    def run_mic_transcription(self, duration):
        try:
            def callback(msg):
                self.set_status(msg)
                
            text = converter.transcribe_mic_input(duration=duration, progress_callback=callback)
            
            self.transcribed_text_box.delete("1.0", tk.END)
            self.transcribed_text_box.insert(tk.END, text)
            self.set_status("Microphone recording transcription complete.")
            messagebox.showinfo("Success", "Microphone recording transcribed successfully!")
        except Exception as e:
            self.set_status("Microphone transcription failed.")
            messagebox.showerror("Recording Transcription Failed", str(e))
        finally:
            self.btn_transcribe.config(state="normal")
            
    # ── Text to PDF Compilation ────────────────────────────────────────────────
    def save_pdf_file(self):
        text = self.transcribed_text_box.get("1.0", tk.END).strip()
        if not text:
            messagebox.showerror("Error", "No transcription text found. Please record or transcribe first.")
            return
            
        title = self.doc_title_entry.get().strip() or "Transcribed Speech Document"
        
        output_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Documents", "*.pdf")],
            initialfile="speech_document"
        )
        if not output_path:
            return
            
        self.btn_save_pdf.config(state="disabled")
        self.set_status("Generating PDF...")
        
        try:
            def callback(msg):
                self.set_status(msg)
                
            converter.save_text_to_pdf(text, output_path, title, progress_callback=callback)
            messagebox.showinfo("Success", f"PDF Document saved successfully:\n{output_path}")
        except Exception as e:
            self.set_status("PDF compilation failed.")
            messagebox.showerror("PDF Saving Failed", str(e))
        finally:
            self.btn_save_pdf.config(state="normal")
            self.set_status("Ready")

if __name__ == "__main__":
    app = App()
    app.mainloop()
