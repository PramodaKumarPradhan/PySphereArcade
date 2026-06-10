"""
ARIA Voice Assistant — Flask Web Server
REST API + WebSocket for real-time communication with the UI dashboard.
"""

import json
import os
import sys
import logging
import threading
import webbrowser
import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)
# Force UTF-8 output on Windows console
import io
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

logger = logging.getLogger('ARIA')

# Ensure we can import from the project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# Load configuration
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = json.load(f)

# Initialize Flask
UI_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui')
app = Flask(__name__, static_folder=UI_FOLDER, template_folder=UI_FOLDER)
app.config['SECRET_KEY'] = 'aria-secret-key-2024'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='threading')

# Initialize Assistant Core
from assistant_core import AssistantCore
assistant = AssistantCore(config, socketio)
logger.info("[OK] ARIA Assistant Core loaded successfully!")


# ── Static Files ────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory(UI_FOLDER, 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(UI_FOLDER, filename)


# ── REST API ────────────────────────────────────────────────────────────────

@app.route('/api/command', methods=['POST'])
def handle_command():
    """Process a text/voice command"""
    data = request.get_json(silent=True) or {}
    text = data.get('text', '').strip()
    language = data.get('language', None)

    if not text:
        return jsonify({'success': False, 'response': 'No command provided', 'response_hi': 'कोई कमांड नहीं दी'}), 400

    result = assistant.process_command(text, language)
    return jsonify(result)


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current system/assistant status for dashboard"""
    return jsonify(assistant.get_system_status())


@app.route('/api/speak', methods=['POST'])
def speak_text():
    """TTS — speak given text"""
    data = request.get_json(silent=True) or {}
    text = data.get('text', '')
    lang = data.get('lang', assistant.current_language)
    if text:
        threading.Thread(
            target=assistant.synthesizer.speak,
            args=(text, lang),
            daemon=True
        ).start()
    return jsonify({'status': 'speaking'})


@app.route('/api/stop-speak', methods=['POST'])
def stop_speak():
    """Stop current TTS"""
    assistant.synthesizer.stop()
    return jsonify({'status': 'stopped'})


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    safe_config = {k: v for k, v in config.items() if k != 'ai' or not v.get('gemini_api_key')}
    return jsonify(safe_config)


@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration"""
    data = request.get_json(silent=True) or {}
    # Only allow updating safe fields
    allowed = ['voice', 'features', 'ui', 'language']
    for key in allowed:
        if key in data:
            config[key].update(data[key])
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return jsonify({'status': 'ok', 'message': 'Config updated'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get conversation history"""
    return jsonify({'history': assistant.conversation_history[-20:]})


@app.route('/api/history', methods=['DELETE'])
def clear_history():
    """Clear conversation history"""
    assistant.conversation_history.clear()
    return jsonify({'status': 'ok'})


@app.route('/api/quick-commands', methods=['GET'])
def quick_commands():
    """Get quick command tiles for the UI"""
    commands = [
        {'id': 'time', 'label': 'Time', 'label_hi': 'समय', 'command': 'what time is it', 'icon': '🕐'},
        {'id': 'weather', 'label': 'Weather', 'label_hi': 'मौसम', 'command': 'weather in Delhi', 'icon': '☁️'},
        {'id': 'news', 'label': 'News', 'label_hi': 'समाचार', 'command': 'open news', 'icon': '📰'},
        {'id': 'youtube', 'label': 'YouTube', 'label_hi': 'यूट्यूब', 'command': 'open youtube', 'icon': '▶️'},
        {'id': 'screenshot', 'label': 'Screenshot', 'label_hi': 'स्क्रीनशॉट', 'command': 'take screenshot', 'icon': '📸'},
        {'id': 'volume_up', 'label': 'Vol Up', 'label_hi': 'आवाज़+', 'command': 'volume up', 'icon': '🔊'},
        {'id': 'volume_down', 'label': 'Vol Down', 'label_hi': 'आवाज़-', 'command': 'volume down', 'icon': '🔉'},
        {'id': 'mute', 'label': 'Mute', 'label_hi': 'म्यूट', 'command': 'mute', 'icon': '🔇'},
        {'id': 'notepad', 'label': 'Notepad', 'label_hi': 'नोटपैड', 'command': 'open notepad', 'icon': '📝'},
        {'id': 'calculator', 'label': 'Calculator', 'label_hi': 'कैलकुलेटर', 'command': 'open calculator', 'icon': '🔢'},
        {'id': 'gmail', 'label': 'Gmail', 'label_hi': 'जीमेल', 'command': 'open gmail', 'icon': '📧'},
        {'id': 'whatsapp', 'label': 'WhatsApp', 'label_hi': 'व्हाट्सएप', 'command': 'open whatsapp', 'icon': '💬'},
        {'id': 'spotify', 'label': 'Spotify', 'label_hi': 'स्पॉटिफाई', 'command': 'open spotify', 'icon': '🎵'},
        {'id': 'night_mode', 'label': 'Night Mode', 'label_hi': 'नाइट मोड', 'command': 'night mode on', 'icon': '🌙'},
        {'id': 'battery', 'label': 'Battery', 'label_hi': 'बैटरी', 'command': 'battery status', 'icon': '🔋'},
        {'id': 'lock', 'label': 'Lock PC', 'label_hi': 'लॉक', 'command': 'lock screen', 'icon': '🔒'},
    ]
    return jsonify({'commands': commands})


# ── WebSocket Events ─────────────────────────────────────────────────────────

@socketio.on('connect')
def on_connect():
    logger.info(f"Client connected: {request.sid}")
    emit('status', {'connected': True, 'assistant': 'ARIA'})


@socketio.on('disconnect')
def on_disconnect():
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on('command')
def on_command(data):
    """Handle real-time voice command via WebSocket"""
    text = data.get('text', '')
    language = data.get('language', None)
    if text:
        result = assistant.process_command(text, language)
        emit('response', result)


@socketio.on('listen_start')
def on_listen_start(data):
    """Start listening via Python STT (if microphone available)"""
    language = data.get('language', 'en')
    if not assistant.recognizer.available:
        emit('listen_result', {
            'error': 'Microphone not available in Python. Use browser voice input.',
            'use_browser': True
        })
        return

    def _listen():
        result = assistant.recognizer.listen(language=language)
        socketio.emit('listen_result', result)

    threading.Thread(target=_listen, daemon=True).start()
    emit('listening', {'status': 'started'})


@socketio.on('ping')
def on_ping():
    emit('pong', {'time': datetime.datetime.now().isoformat()})


# ── Main Entry ───────────────────────────────────────────────────────────────

def print_banner():
    port = config.get('server', {}).get('port', 7777)
    sep = '=' * 58
    ai_status = 'Gemini AI [ON]' if assistant._gemini_model else 'Rule-based only'
    mic_status = '[READY]' if assistant.recognizer.available else '[Browser voice input]'
    print(f"\n{sep}")
    print("  ARIA -- Bilingual Voice Assistant")
    print("  English + Hindi | Office, Home & Laptop")
    print(sep)
    print(f"  Dashboard  : http://localhost:{port}")
    print(f"  AI Brain   : {ai_status}")
    print(f"  Microphone : {mic_status}")
    print(f"  TTS Engine : pyttsx3 + gTTS")
    print(sep)
    print("  Press Ctrl+C to stop\n")


if __name__ == '__main__':
    port = config.get('server', {}).get('port', 7777)
    auto_open = config.get('server', {}).get('auto_open_browser', True)

    print_banner()

    if auto_open:
        def _open_browser():
            import time
            time.sleep(1.5)
            webbrowser.open(f'http://localhost:{port}')
        threading.Thread(target=_open_browser, daemon=True).start()

    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False,
        log_output=False,
        allow_unsafe_werkzeug=True
    )
