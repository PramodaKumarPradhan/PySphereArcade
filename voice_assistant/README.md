# ARIA — Bilingual Voice Assistant
## English + Hindi | Office, Home & Laptop

> 🎙️ **A**rtificial **R**esponsive **I**ntelligent **A**ssistant — by Pramod Kumar Pradhan

---

## ✨ Features

| Category | Commands |
|---|---|
| 💻 **Laptop** | Open/close apps, volume, brightness, screenshot, sleep, lock, shutdown |
| 🏢 **Office** | Word, Excel, PowerPoint, Outlook, reminders, timers, notes, calendar |
| 🌐 **Web** | Google, YouTube, Wikipedia, weather, maps, news, any website |
| 🎵 **Media** | Play/pause, next/prev, Spotify, VLC, YouTube Music |
| 📁 **Files** | Open downloads/documents/desktop, find files, disk usage |
| 📧 **Communication** | Gmail, Outlook, WhatsApp, Teams, Zoom, Skype, Google Meet |
| 🏠 **Home** | Night mode, water reminders, focus mode, environment check |
| 🤖 **AI Brain** | Gemini AI for natural language Q&A (optional) |
| 🌐 **Bilingual** | Full English + Hindi support with auto language detection |

---

## 🚀 Quick Start

### 1. Prerequisites
- **Python 3.9+** — [Download here](https://www.python.org/downloads/)
- **Chrome or Edge** browser (for voice recognition)
- **Microphone** (optional — you can also type commands)

### 2. Run ARIA

Simply double-click **`run.bat`** — it will:
1. Create a virtual environment
2. Install all dependencies automatically
3. Open the dashboard at `http://localhost:7777`

### 3. Manual Setup (optional)

```bash
cd voice_assistant
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

---

## 🎙️ How to Use

| Method | How |
|---|---|
| **Voice** | Click the 🎙️ mic button OR press `Ctrl+Space` |
| **Keyboard** | Type in the text box and press Enter |
| **Quick Tiles** | Click any tile in the left panel |
| **Command Examples** | Click any example in the right panel |

---

## 💬 Sample Commands

### English
- *"What time is it?"* / *"What's today's date?"*
- *"Open Notepad"* / *"Open Word"* / *"Open Chrome"*
- *"Search YouTube for lo-fi music"*
- *"What's the weather in Mumbai?"*
- *"Take a screenshot"*
- *"Volume up 20"* / *"Mute"*
- *"Set a timer for 10 minutes"*
- *"Remind me to drink water in 30 minutes"*
- *"Night mode on"* / *"Lock screen"*
- *"Battery status"* / *"System info"*
- *"Open Gmail"* / *"Open WhatsApp"*
- *"Tell me a joke"*
- *"Calculate 25 * 48"*

### हिंदी (Hindi)
- *"समय बताओ"* / *"आज की तारीख"*
- *"Notepad खोलो"* / *"कैलकुलेटर खोलो"*
- *"आवाज़ बढ़ाओ"* / *"आवाज़ कम करो"* / *"म्यूट करो"*
- *"स्क्रीनशॉट लो"*
- *"मौसम बताओ"*
- *"नाइट मोड चालू करो"*
- *"बैटरी बताओ"*
- *"जोक सुनाओ"*
- *"YouTube पर गाना लगाओ"*
- *"WhatsApp खोलो"*
- *"Gmail खोलो"*

---

## ⚙️ Configuration

Edit **`config.json`** to customize:

```json
{
  "assistant": { "name": "Aria" },
  "server":    { "port": 7777, "auto_open_browser": true },
  "language":  { "default": "en" },
  "voice":     { "rate_en": 165, "rate_hi": 145, "volume": 0.92 },
  "ai":        { "gemini_api_key": "YOUR_KEY_HERE" }
}
```

### 🤖 Enable AI Brain (Gemini)
1. Get a free API key from [Google AI Studio](https://aistudio.google.com/)
2. Add it to `config.json` → `ai.gemini_api_key`
3. Restart ARIA

---

## 🔧 Troubleshooting

| Issue | Solution |
|---|---|
| *Mic not working* | Use Chrome/Edge; allow microphone permission |
| *PyAudio install fails* | Run: `pip install pipwin && pipwin install pyaudio` |
| *App won't start* | Check Python 3.9+ is installed; run `pip install -r requirements.txt` |
| *Hindi TTS sounds robotic* | Enable Gemini API; or install Hindi voice in Windows Settings → Time & Language → Language |
| *Volume/brightness not working* | Run ARIA as Administrator |

---

## 📁 Project Structure

```
voice_assistant/
├── app.py               # Flask web server
├── assistant_core.py    # Command router + AI brain
├── config.json          # Settings
├── requirements.txt     # Python dependencies
├── run.bat              # Windows launcher
├── skills/              # Feature modules
│   ├── system_control.py
│   ├── office_tasks.py
│   ├── web_tasks.py
│   ├── media_control.py
│   ├── home_control.py
│   ├── information.py
│   ├── file_manager.py
│   └── communication.py
├── language/            # STT/TTS/Translation
│   ├── recognizer.py
│   ├── synthesizer.py
│   └── translator.py
└── ui/                  # Web dashboard
    ├── index.html
    ├── style.css
    └── app.js
```

---

*Built with ❤️ using Python, Flask, and modern web technologies*
*Pramod Kumar Pradhan — 2026*
