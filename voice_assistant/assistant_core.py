"""
ARIA Voice Assistant — Core Brain
Routes voice commands to appropriate skills in English and Hindi.
Integrates Gemini AI for natural language fallback.
"""

import re
import json
import logging
import datetime
import threading

logger = logging.getLogger(__name__)

from language.recognizer import SpeechRecognizer
from language.synthesizer import SpeechSynthesizer
from language.translator import LanguageTranslator
from skills.system_control import SystemControl
from skills.office_tasks import OfficeTasks
from skills.web_tasks import WebTasks
from skills.media_control import MediaControl
from skills.home_control import HomeControl
from skills.information import Information
from skills.file_manager import FileManager
from skills.communication import Communication
from skills.pc_automation import PcAutomation

try:
    import google.genai as genai
    from google.genai import types as genai_types
    GEMINI_AVAILABLE = True
except ImportError:
    try:
        import google.generativeai as genai
        genai_types = None
        GEMINI_AVAILABLE = True
    except ImportError:
        GEMINI_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class AssistantCore:
    """
    Central command router for ARIA.
    Detects language → normalizes command → routes to skill → responds.
    """

    def __init__(self, config: dict, socketio=None):
        self.config = config
        self.socketio = socketio
        self.current_language = config.get('language', {}).get('default', 'en')
        self.conversation_history = []
        self._gemini_model = None
        self._lock = threading.Lock()

        # Initialize language components
        self.recognizer = SpeechRecognizer(config)
        self.synthesizer = SpeechSynthesizer(config)
        self.translator = LanguageTranslator(config)

        # Initialize skills
        self.system = SystemControl(config)
        self.office = OfficeTasks(config)
        self.web = WebTasks(config)
        self.media = MediaControl(config)
        self.home = HomeControl(config)
        self.info = Information(config)
        self.files = FileManager(config)
        self.comms = Communication(config)
        self.pc = PcAutomation(config)

        # Setup Gemini AI
        self._setup_gemini()

        logger.info("AssistantCore initialized — ARIA is ready! 🎙️")

    def _setup_gemini(self):
        """Initialize Gemini AI model if API key is available"""
        api_key = self.config.get('ai', {}).get('gemini_api_key', '')
        if api_key and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=api_key)
                model_name = self.config.get('ai', {}).get('model', 'gemini-1.5-flash')
                self._gemini_model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=(
                        "You are ARIA, a friendly and helpful voice assistant that supports "
                        "both English and Hindi. Keep responses concise (1-3 sentences max), "
                        "natural, and conversational. Never use markdown formatting. "
                        "Respond in the same language as the user's query."
                    )
                )
                logger.info(f"Gemini AI ready: {model_name}")
            except Exception as e:
                logger.warning(f"Gemini setup failed: {e}")
                self._gemini_model = None

    # ── Command Processing ───────────────────────────────────────────────────

    def process_command(self, text: str, language: str = None) -> dict:
        """
        Main entry point. Process a voice/text command.
        Returns: {'response': str, 'response_hi': str, 'action': str, 'success': bool}
        """
        if not text or not text.strip():
            return self._make_response("I didn't catch that. Please try again.",
                                       "मैं समझ नहीं पाया। कृपया फिर बोलें।", False)

        # Detect language if not specified
        detected_lang = language or self.translator.detect_language(text)
        self.current_language = detected_lang

        # Normalize: translate Hindi or Malay to English for routing
        normalized = text.strip().lower()
        if detected_lang == 'hi':
            normalized = self.translator.hindi_to_english_command(text)
            logger.info(f"Hindi '{text}' → English '{normalized}'")
        elif detected_lang == 'ms':
            normalized = self.translator.translate(text, src='ms', dest='en')
            logger.info(f"Malay '{text}' → English '{normalized}'")

        # Log command
        logger.info(f"Command [{detected_lang}]: '{text}' → normalized: '{normalized}'")

        # Route to appropriate skill
        result = self._route_command(normalized, text, detected_lang)

        # Ensure response is translated to the detected language
        if detected_lang != 'en' and f'response_{detected_lang}' not in result:
            result[f'response_{detected_lang}'] = self.translator.get_response_in_language(result.get('response', ''), detected_lang)

        # Add to conversation history
        self._add_to_history(text, result.get(f'response_{detected_lang}', result.get('response', '')), detected_lang)

        # Emit to UI via SocketIO
        if self.socketio:
            self.socketio.emit('command_result', result)

        # Speak the response
        speak_text = result.get(f'response_{detected_lang}' if detected_lang != 'en' else 'response', '')
        if speak_text:
            self.synthesizer.speak(speak_text, detected_lang)

        return result

    def _route_command(self, normalized: str, original: str, lang: str) -> dict:
        """Route normalized command to the correct skill handler"""
        cmd = normalized.strip().lower()

        # ── Meta / Assistant Commands ──────────────────────────────────────
        if any(w in cmd for w in ['hello', 'hi aria', 'hey aria', 'good morning',
                                   'good afternoon', 'good evening', 'good night',
                                   'namaste', 'namaskar']):
            return self.info.greet(lang)

        if any(w in cmd for w in ['help', 'what can you do', 'commands', 'guide', 'list commands']):
            return self.info.help_menu()

        if any(w in cmd for w in ['thank', 'thanks', 'shukriya', 'dhanyawad']):
            return self._make_response(
                "You're welcome! Always here to help you. 😊",
                "आपका स्वागत है! हमेशा आपकी मदद के लिए यहाँ हूँ। 😊"
            )

        if any(w in cmd for w in ['goodbye', 'bye', 'exit', 'quit', 'close aria',
                                   'alvida', 'shut down aria']):
            return self._make_response(
                "Goodbye! Have a wonderful day! See you soon! 👋",
                "अलविदा! आपका दिन शानदार हो! जल्द मिलते हैं! 👋",
                action='exit'
            )

        if any(w in cmd for w in ['speak in hindi', 'switch to hindi', 'hindi mein bolo']):
            self.current_language = 'hi'
            return self._make_response(
                "Switched to Hindi mode.",
                "ठीक है! अब मैं हिंदी में बात करूँगा। 🇮🇳"
            )

        if any(w in cmd for w in ['speak in english', 'switch to english', 'english mein bolo']):
            self.current_language = 'en'
            return self._make_response(
                "Switched to English mode! 🇬🇧",
                "English mode चालू किया! 🇬🇧"
            )

        if 'what is your name' in cmd or 'your name' in cmd or 'naam kya hai' in cmd:
            name = self.config.get('assistant', {}).get('name', 'Aria')
            return self._make_response(
                f"I'm {name}, your intelligent bilingual voice assistant! 🎙️",
                f"मैं {name} हूँ, आपका बुद्धिमान द्विभाषी वॉइस असिस्टेंट! 🎙️"
            )

        if 'who made you' in cmd or 'who created you' in cmd or 'kisne banaya' in cmd:
            return self._make_response(
                "I was created by Pramod Kumar Pradhan using Python and AI technologies. 🚀",
                "मुझे Pramod Kumar Pradhan ने Python और AI तकनीक से बनाया है। 🚀"
            )

        # ── Time & Date ───────────────────────────────────────────────────
        if any(w in cmd for w in ['time', 'what time', 'baje hain', 'baj rahe']):
            return self.info.tell_time()

        if any(w in cmd for w in ['date', 'today', 'day', 'tarikh', 'aaj']):
            if 'weather' not in cmd:
                return self.info.tell_date()

        # ── Jokes ─────────────────────────────────────────────────────────
        if any(w in cmd for w in ['joke', 'funny', 'laugh', 'chutkula', 'sunao']):
            return self.info.tell_joke(lang)

        # ── Calculator ────────────────────────────────────────────────────
        calc_match = re.search(r'(?:calculate|compute|what is|solve|what\'?s)\s+(.+)', cmd)
        if calc_match:
            expr = calc_match.group(1)
            if any(op in expr for op in ['+', '-', '*', '/', '%', 'x', 'plus', 'minus', 'times', 'divided']):
                expr = (expr.replace('plus', '+').replace('minus', '-')
                           .replace('times', '*').replace('x', '*')
                           .replace('divided by', '/').replace('into', '*'))
                return self.info.calculate(expr)

        # ── System Info ───────────────────────────────────────────────────
        if any(w in cmd for w in ['system info', 'system status', 'cpu', 'ram', 'memory usage']):
            return self.info.get_system_info()

        if any(w in cmd for w in ['battery', 'charge', 'battery status', 'baatri']):
            return self.info.battery_status()

        # ── Volume ────────────────────────────────────────────────────────
        if any(w in cmd for w in ['volume up', 'increase volume', 'louder', 'awaz badhao', 'turn up']):
            step = self._extract_number(cmd) or 10
            return self.system.volume_up(step)

        if any(w in cmd for w in ['volume down', 'decrease volume', 'quieter', 'awaz kam', 'turn down']):
            step = self._extract_number(cmd) or 10
            return self.system.volume_down(step)

        if any(w in cmd for w in ['mute', 'silence', 'mute volume', 'bandh karo awaz']):
            return self.system.mute_volume()

        vol_match = re.search(r'(?:set volume|volume)\s+(?:to\s+)?(\d+)', cmd)
        if vol_match:
            return self.system.set_volume(int(vol_match.group(1)))

        # ── Brightness ────────────────────────────────────────────────────
        if any(w in cmd for w in ['brightness up', 'increase brightness', 'brighter']):
            return self.system.brightness_up()

        if any(w in cmd for w in ['brightness down', 'decrease brightness', 'dim']):
            return self.system.brightness_down()

        # ── Screenshot ────────────────────────────────────────────────────
        if any(w in cmd for w in ['screenshot', 'screen shot', 'capture screen', 'screenshoot']):
            return self.system.take_screenshot()

        # ── Power ─────────────────────────────────────────────────────────
        if any(w in cmd for w in ['shutdown', 'shut down', 'turn off', 'power off', 'band karo']):
            if 'cancel' not in cmd:
                return self.system.shutdown()

        if any(w in cmd for w in ['restart', 'reboot', 'restart computer']):
            return self.system.restart()

        if any(w in cmd for w in ['sleep', 'hibernate', 'standby']):
            return self.system.sleep()

        if any(w in cmd for w in ['lock', 'lock screen', 'lock computer']):
            return self.system.lock_screen()

        if any(w in cmd for w in ['cancel shutdown', 'abort shutdown', 'stop shutdown']):
            return self.system.cancel_shutdown()

        if any(w in cmd for w in ['minimize', 'show desktop', 'desktop dikhao']):
            return self.system.minimize_all()

        # ── Open Application / Website ─────────────────────────────────────
        # "Open notepad and write Hello World"
        open_and_write = re.search(
            r'open\s+(\S+(?:\s+\S+)?)\s+and\s+(?:write|type|say)\s+(.+)', cmd)
        if open_and_write:
            app = open_and_write.group(1).strip()
            content = open_and_write.group(2).strip()
            return self.pc.open_and_write(app, content)

        # "Open notepad and write" (content in original)
        open_write2 = re.search(
            r'open\s+(notepad|word|wordpad|editor)\s+(?:and\s+)?(?:write|type)\s+(.+)', cmd)
        if open_write2:
            app = open_write2.group(1).strip()
            content = open_write2.group(2).strip()
            if app == 'notepad':
                return self.pc.open_notepad_and_write(content)
            return self.pc.open_and_write(app, content)

        open_match = re.search(r'open\s+(.+?)(?:\s+app(?:lication)?)?$', cmd)
        if open_match:
            app = open_match.group(1).strip()
            # Check website map first
            from skills.pc_automation import WEBSITE_MAP
            if app in WEBSITE_MAP or any(k in app for k in WEBSITE_MAP):
                return self.pc.open_website(app)
            if app in self.web.QUICK_SITES or '.' in app:
                return self.web.open_website(app)
            # Use PcAutomation for smart app finding
            return self.pc.open_application(app)

        # ── Go to / Browse Website ────────────────────────────────────────
        goto_match = re.search(
            r'(?:go to|browse|visit|navigate to|take me to)\s+(.+)', cmd)
        if goto_match:
            site = goto_match.group(1).strip()
            return self.pc.open_website(site)

        # "website <name>" or "open website <name>"
        website_match = re.search(r'website\s+(.+)', cmd)
        if website_match:
            return self.pc.open_website(website_match.group(1).strip())

        # ── Type / Write / Dictate text ───────────────────────────────────
        # "type hello world" / "write hello world"
        type_match = re.search(
            r'^(?:type|write|dictate|say|input)\s+(?:in|into\s+\w+\s+)?(.+)', cmd)
        if type_match:
            content = type_match.group(1).strip()
            return self.pc.type_text(content)

        # "write in notepad: <content>"
        write_in_match = re.search(
            r'(?:write|type)\s+in\s+(\w+)[:\s]+(.+)', cmd)
        if write_in_match:
            app = write_in_match.group(1).strip()
            content = write_in_match.group(2).strip()
            if app == 'notepad':
                return self.pc.open_notepad_and_write(content)
            return self.pc.open_and_write(app, content)

        # "create a file named <x> with content <y>"
        create_file_match = re.search(
            r'create\s+(?:a\s+)?(?:file|document|note)\s+(?:named?|called)\s+(\S+)\s+'   
            r'(?:with\s+content|containing|with|saying)\s+(.+)', cmd)
        if create_file_match:
            fname = create_file_match.group(1).strip()
            content = create_file_match.group(2).strip()
            return self.pc.create_and_save_file(fname, content)

        # "save this as <filename>"
        save_as_match = re.search(r'save\s+(?:this\s+)?(?:as|to)\s+(\S+)', cmd)
        if save_as_match:
            fname = save_as_match.group(1).strip()
            return self.pc.create_and_save_file(fname, '')

        # ── Close Application ─────────────────────────────────────────────
        close_match = re.search(r'close\s+(.+)', cmd)
        if close_match:
            app = close_match.group(1).strip()
            return self.pc.close_application(app)

        # ── Kill app ──────────────────────────────────────────────────────
        kill_match = re.search(r'(?:kill|force close|terminate)\s+(.+)', cmd)
        if kill_match:
            return self.pc.close_application(kill_match.group(1).strip())

        # ── Search ────────────────────────────────────────────────────────
        yt_match = re.search(r'(?:youtube|play|search youtube for)\s+(.+?)(?:\s+on youtube)?$', cmd)
        if yt_match and ('youtube' in cmd or 'play' in cmd):
            return self.media.play_on_youtube(yt_match.group(1).strip())

        yt_search = re.search(r'(?:search|find)\s+(.+?)\s+on youtube', cmd)
        if yt_search:
            return self.web.youtube_search(yt_search.group(1))

        google_match = re.search(r'(?:search|google|look up|find)\s+(.+?)(?:\s+on google)?$', cmd)
        if google_match and ('google' in cmd or 'search' in cmd or 'look up' in cmd):
            return self.web.google_search(google_match.group(1))

        wiki_match = re.search(r'(?:wikipedia|wiki|what is|who is|tell me about)\s+(.+)', cmd)
        if wiki_match:
            return self.web.wikipedia_search(wiki_match.group(1), lang)

        # ── Weather ───────────────────────────────────────────────────────
        weather_match = re.search(r"weather(?:\s+in\s+|\s+of\s+|\s+for\s+)?(.+)?", cmd)
        if weather_match:
            city = (weather_match.group(1) or 'Delhi').strip()
            if not city or city in ['today', 'now', 'current']:
                city = 'Delhi'
            return self.web.get_weather(city)

        # ── Maps ──────────────────────────────────────────────────────────
        maps_match = re.search(r'(?:open maps|directions|navigate to|maps for)\s*(.*)', cmd)
        if maps_match:
            return self.web.open_maps(maps_match.group(1).strip())

        # ── Media ─────────────────────────────────────────────────────────
        if any(w in cmd for w in ['play pause', 'pause', 'resume music', 'resume']):
            return self.media.play_pause()

        if any(w in cmd for w in ['next', 'skip', 'next song', 'next track']):
            return self.media.next_track()

        if any(w in cmd for w in ['previous', 'prev', 'last song', 'go back']):
            return self.media.previous_track()

        if any(w in cmd for w in ['stop music', 'stop media', 'stop playing']):
            return self.media.stop_media()

        if 'spotify' in cmd:
            if 'search' in cmd or 'play' in cmd:
                sp_match = re.search(r'(?:spotify|play on spotify|search spotify for)\s+(.+)', cmd)
                if sp_match:
                    return self.media.play_on_spotify_search(sp_match.group(1))
            return self.media.open_spotify()

        if 'vlc' in cmd:
            return self.media.open_vlc()

        if any(w in cmd for w in ['youtube music', 'music on youtube']):
            return self.media.open_youtube_music()

        # ── Office ────────────────────────────────────────────────────────
        if any(w in cmd for w in ['word', 'microsoft word', 'word document']):
            return self.office.open_office_app('word')

        if any(w in cmd for w in ['excel', 'spreadsheet', 'microsoft excel']):
            return self.office.open_office_app('excel')

        if any(w in cmd for w in ['powerpoint', 'presentation', 'ppt', 'slides']):
            return self.office.open_office_app('powerpoint')

        if any(w in cmd for w in ['outlook email', 'microsoft outlook']):
            return self.office.open_office_app('outlook')

        if any(w in cmd for w in ['teams', 'microsoft teams']):
            return self.comms.open_teams()

        # ── Timer ─────────────────────────────────────────────────────────
        timer_match = re.search(
            r'(?:set a? ?timer|timer)\s+(?:for\s+)?(\d+)\s*(hour|hr|minute|min|second|sec)',
            cmd
        )
        if timer_match:
            amount = int(timer_match.group(1))
            unit = timer_match.group(2).lower()
            seconds = amount * 3600 if 'hour' in unit else (
                amount * 60 if 'min' in unit else amount
            )
            return self.office.set_timer(seconds, callback=self._notification_callback)

        # ── Reminder ──────────────────────────────────────────────────────
        remind_match = re.search(
            r'remind me(?: to)?\s+(.+?)\s+in\s+(\d+)\s*(hour|hr|minute|min)',
            cmd
        )
        if remind_match:
            message = remind_match.group(1).strip()
            amount = int(remind_match.group(2))
            unit = remind_match.group(3).lower()
            seconds = amount * 3600 if 'hour' in unit else amount * 60
            return self.office.set_reminder(message, seconds,
                                             callback=self._notification_callback)

        # ── Notes ─────────────────────────────────────────────────────────
        note_match = re.search(r'(?:take a note|note|write down|save note)[:\s]+(.+)', cmd)
        if note_match:
            return self.office.create_note(note_match.group(1).strip())

        if any(w in cmd for w in ['open notes', 'my notes', 'notes folder']):
            return self.office.open_notes_folder()

        # ── Calendar ─────────────────────────────────────────────────────
        if any(w in cmd for w in ['calendar', 'schedule', 'agenda']):
            return self.office.open_calendar()

        if any(w in cmd for w in ['today schedule', 'what day', 'what day is it']):
            return self.office.tell_schedule()

        # ── File Manager ──────────────────────────────────────────────────
        if any(w in cmd for w in ['downloads', 'download folder']):
            return self.files.open_downloads()

        if any(w in cmd for w in ['documents', 'document folder', 'my documents']):
            return self.files.open_documents()

        if any(w in cmd for w in ['desktop', 'show desktop files']):
            return self.files.open_desktop()

        if any(w in cmd for w in ['pictures', 'photos', 'images folder']):
            return self.files.open_pictures()

        if any(w in cmd for w in ['file explorer', 'explorer', 'my computer', 'this pc']):
            return self.files.open_file_explorer()

        if any(w in cmd for w in ['disk usage', 'storage', 'disk space', 'free space']):
            return self.files.disk_usage()

        find_match = re.search(r'find (?:file |folder )?(.+)', cmd)
        if find_match:
            return self.files.find_file(find_match.group(1).strip())

        # ── Communication ─────────────────────────────────────────────────
        if any(w in cmd for w in ['gmail', 'google mail']):
            return self.comms.open_gmail()

        if 'outlook' in cmd and 'teams' not in cmd:
            return self.comms.open_outlook()

        compose_match = re.search(r'compose email|new email|write email', cmd)
        if compose_match:
            return self.comms.compose_email()

        if any(w in cmd for w in ['whatsapp', 'whatsap', 'whats app']):
            return self.comms.open_whatsapp()

        if 'zoom' in cmd:
            return self.comms.open_zoom()

        if 'skype' in cmd:
            return self.comms.open_skype()

        if 'telegram' in cmd:
            return self.comms.open_telegram()

        if any(w in cmd for w in ['google meet', 'meet', 'video call']):
            return self.comms.start_google_meet()

        # ── Home / Environment ────────────────────────────────────────────
        if any(w in cmd for w in ['night mode on', 'enable night mode', 'night light on']):
            return self.home.night_mode_on()

        if any(w in cmd for w in ['night mode off', 'disable night mode', 'night light off']):
            return self.home.night_mode_off()

        if any(w in cmd for w in ['water reminder', 'remind water', 'hydration reminder']):
            return self.home.start_water_reminders(callback=self._notification_callback)

        if any(w in cmd for w in ['focus mode', 'do not disturb', 'dnd']):
            return self.home.focus_mode()

        if any(w in cmd for w in ['empty recycle bin', 'clear trash', 'recycle bin']):
            return self.home.empty_recycle_bin()

        if any(w in cmd for w in ['environment', 'status check', 'how am i doing']):
            return self.home.check_environment()

        shutdown_schedule = re.search(r'(?:schedule|auto)\s*shutdown\s+(?:in\s+)?(\d+)\s*(?:minute|min)?', cmd)
        if shutdown_schedule:
            mins = int(shutdown_schedule.group(1))
            return self.home.schedule_shutdown(mins)

        # ── Connectivity Toggles ──────────────────────────────────────────
        if any(w in cmd for w in ['wifi on', 'turn on wifi', 'enable wifi', 'start wifi']):
            return self.system.set_wifi(True)

        if any(w in cmd for w in ['wifi off', 'turn off wifi', 'disable wifi', 'stop wifi']):
            return self.system.set_wifi(False)

        if any(w in cmd for w in ['bluetooth on', 'turn on bluetooth', 'enable bluetooth', 'start bluetooth']):
            return self.system.set_bluetooth(True)

        if any(w in cmd for w in ['bluetooth off', 'turn off bluetooth', 'disable bluetooth', 'stop bluetooth']):
            return self.system.set_bluetooth(False)

        if any(w in cmd for w in ['airplane mode on', 'enable airplane mode', 'turn on airplane mode']):
            return self.system.set_airplane_mode(True)

        if any(w in cmd for w in ['airplane mode off', 'disable airplane mode', 'turn off airplane mode']):
            return self.system.set_airplane_mode(False)

        # ── Fun / Utility ─────────────────────────────────────────────────
        if any(w in cmd for w in ['flip a coin', 'toss a coin', 'coin toss', 'coin flip']):
            return self.info.flip_coin()

        if any(w in cmd for w in ['roll a die', 'roll a dice', 'roll die', 'roll dice']):
            return self.info.roll_die()

        if any(w in cmd for w in ['tell me a fact', 'tell a fact', 'interesting fact', 'tell fact', 'facts']):
            return self.info.tell_fact(lang)

        # ── Stock Price ───────────────────────────────────────────────────
        stock_match = re.search(r'(?:stock price of|price of|stock of|share price of)\s+(\w+)', cmd)
        if stock_match:
            symbol = stock_match.group(1).strip()
            return self.web.get_stock_price(symbol)

        # ── Umbrella / Rain Check ─────────────────────────────────────────
        if any(w in cmd for w in ['need an umbrella', 'need umbrella', 'will it rain', 'is it raining', 'should i take an umbrella']):
            city_match = re.search(r'(?:in|for|at)\s+(\S+)', cmd)
            city = city_match.group(1).strip() if city_match else 'Delhi'
            return self.web.check_rain_advice(city)

        # ── Smart Home Control ────────────────────────────────────────────
        smart_home_match = re.search(r'(?:turn|switch)\s+(on|off)\s+(?:the\s+)?(.+)', cmd)
        if smart_home_match and any(w in cmd for w in ['light', 'fan', 'ac', 'cooler', 'lamp', 'bulb', 'switch', 'led']):
            state = smart_home_match.group(1).strip()
            device = smart_home_match.group(2).strip()
            return self.home.control_smart_home(device, state)

        temp_match = re.search(r'(?:set|change)\s+(?:the\s+)?(?:thermostat|temp|temperature)\s+(?:to\s+)?(\d+)', cmd)
        if temp_match:
            val = temp_match.group(1).strip()
            return self.home.control_smart_home('thermostat', 'set', val)

        # ── Website shortcuts ─────────────────────────────────────────────
        for site_key in self.web.QUICK_SITES:
            if site_key in cmd and any(w in cmd for w in ['open', 'go to', 'launch', 'website']):
                return self.web.open_website(site_key)

        # ── Task Manager / Settings ───────────────────────────────────────
        if any(w in cmd for w in ['task manager', 'processes', 'running apps']):
            return self.system.open_task_manager()

        if any(w in cmd for w in ['settings', 'windows settings', 'preferences']):
            return self.system.open_settings()

        # ── List apps ────────────────────────────────────────────────────
        if any(w in cmd for w in ['list apps', 'installed apps', 'what apps', 'show apps']):
            return self.pc.list_installed_apps()

        if any(w in cmd for w in ['running apps', 'open apps', 'what is running']):
            return self.pc.list_running_apps()

        # ── Window Management ─────────────────────────────────────────────
        if any(w in cmd for w in ['switch window', 'alt tab', 'previous window']):
            return self.pc.switch_window()

        if any(w in cmd for w in ['minimize window', 'minimise window', 'shrink window']):
            return self.pc.minimize_window()

        if any(w in cmd for w in ['maximize window', 'maximise window', 'full screen window']):
            return self.pc.maximize_window()

        if any(w in cmd for w in ['close window', 'close this', 'alt f4']):
            return self.pc.close_window()

        if any(w in cmd for w in ['snap left', 'window left', 'move window left']):
            return self.pc.snap_left()

        if any(w in cmd for w in ['snap right', 'window right', 'move window right']):
            return self.pc.snap_right()

        if any(w in cmd for w in ['new desktop', 'virtual desktop']):
            return self.pc.new_virtual_desktop()

        # ── Keyboard Shortcuts ────────────────────────────────────────────
        if any(w in cmd for w in ['save file', 'save it', 'ctrl s', 'save document']):
            return self.pc.save_file()

        if any(w in cmd for w in ['save as', 'save file as']):
            return self.pc.save_file_as()

        if any(w in cmd for w in ['select all', 'ctrl a']):
            return self.pc.select_all()

        if any(w in cmd for w in ['undo', 'ctrl z', 'go back']):
            return self.pc.undo()

        if any(w in cmd for w in ['redo', 'ctrl y']):
            return self.pc.redo()

        if any(w in cmd for w in ['new file', 'new window', 'ctrl n']):
            return self.pc.new_file()

        if any(w in cmd for w in ['open file', 'ctrl o', 'open dialog']):
            return self.pc.open_file_dialog()

        if any(w in cmd for w in ['print', 'print document', 'ctrl p']):
            return self.pc.print_document()

        if any(w in cmd for w in ['press enter', 'hit enter', 'confirm', 'submit']):
            return self.pc.press_enter()

        if any(w in cmd for w in ['press escape', 'escape', 'cancel dialog', 'close popup']):
            return self.pc.press_escape()

        if any(w in cmd for w in ['press tab', 'tab key', 'next field']):
            return self.pc.press_tab()

        find_match2 = re.search(r'find\s+(?:in page\s+)?(.+)', cmd)
        if find_match2 and 'find file' not in cmd:
            return self.pc.find_in_page(find_match2.group(1).strip())

        # ── Clipboard ────────────────────────────────────────────────────
        if any(w in cmd for w in ['copy', 'ctrl c', 'copy selection', 'copy text']):
            return self.pc.copy_selection()

        if any(w in cmd for w in ['paste', 'ctrl v', 'paste here']):
            return self.pc.paste_clipboard()

        if any(w in cmd for w in ['read clipboard', 'what is in clipboard', 'show clipboard']):
            return self.pc.get_clipboard()

        copy_content_match = re.search(r'copy(?:\s+text)?[:\s]+(.+)', cmd)
        if copy_content_match:
            return self.pc.set_clipboard(copy_content_match.group(1).strip())

        # ── Run Command ───────────────────────────────────────────────────
        run_match = re.search(r'run\s+(?:command\s+)?(?:in cmd\s+)?(.+)', cmd)
        if run_match and not any(w in cmd for w in ['run timer', 'run media', 'run script']):
            return self.pc.run_command(run_match.group(1).strip())

        run_dialog_match = re.search(r'run dialog|win r|execute\s+(.+)', cmd)
        if run_dialog_match:
            cmd_text = run_dialog_match.group(1) if run_dialog_match.lastindex else ''
            return self.pc.open_run_dialog(cmd_text.strip() if cmd_text else '')

        # ── AI Fallback ───────────────────────────────────────────────────
        if self._gemini_model and self.config.get('ai', {}).get('enable_ai_fallback', True):
            return self._gemini_fallback(original, lang)

        # ── Default ───────────────────────────────────────────────────────
        return self._make_response(
            f"I'm not sure how to handle that. Say 'help' to see all available commands.",
            f"मैं यह नहीं समझ सका। 'मदद' कहें सभी कमांड देखने के लिए।"
        )

    def _gemini_fallback(self, text: str, language: str) -> dict:
        """Use Gemini AI to handle unrecognized commands"""
        try:
            # Build context from history
            context = ""
            if self.conversation_history:
                recent = self.conversation_history[-3:]
                context = "\n".join([f"User: {h['user']}\nARIA: {h['assistant']}"
                                     for h in recent])

            prompt = f"{context}\nUser: {text}"
            response = self._gemini_model.generate_content(prompt)
            reply = response.text.strip()

            return {
                'success': True,
                'response': reply,
                'response_hi': reply,
                'source': 'gemini'
            }
        except Exception as e:
            logger.error(f"Gemini fallback failed: {e}")
            return self._make_response(
                "I understand what you mean but I'm not able to do that right now. "
                "Try asking something else!",
                "मैं समझ रहा हूँ लेकिन अभी यह नहीं कर सकता। कुछ और बोलें!"
            )

    def _notification_callback(self, data: dict):
        """Handle timer/reminder notifications from skills"""
        msg = data.get('message', '')
        msg_hi = data.get('message_hi', msg)
        if self.socketio:
            self.socketio.emit('notification', {
                'message': msg,
                'message_hi': msg_hi,
                'type': 'reminder'
            })
        # Speak the notification
        speak_text = msg_hi if self.current_language == 'hi' else msg
        self.synthesizer.speak(speak_text, self.current_language)

    def get_system_status(self) -> dict:
        """Get system info for the UI dashboard"""
        status = {
            'assistant_name': self.config.get('assistant', {}).get('name', 'Aria'),
            'language': self.current_language,
            'tts_available': True,
            'stt_available': self.recognizer.available,
            'ai_enabled': self._gemini_model is not None,
            'time': datetime.datetime.now().strftime('%I:%M %p'),
            'date': datetime.datetime.now().strftime('%A, %d %B %Y'),
        }

        if PSUTIL_AVAILABLE:
            try:
                status['cpu'] = psutil.cpu_percent(interval=0.1)
                mem = psutil.virtual_memory()
                status['ram'] = mem.percent
                battery = psutil.sensors_battery()
                if battery:
                    status['battery'] = int(battery.percent)
                    status['charging'] = battery.power_plugged
            except Exception:
                pass

        return status

    def _add_to_history(self, user_text: str, assistant_text: str, language: str):
        """Add exchange to conversation history"""
        max_history = self.config.get('ai', {}).get('max_history', 10)
        self.conversation_history.append({
            'user': user_text,
            'assistant': assistant_text,
            'language': language,
            'timestamp': datetime.datetime.now().isoformat()
        })
        if len(self.conversation_history) > max_history:
            self.conversation_history.pop(0)

    def _extract_number(self, text: str) -> int:
        """Extract first number from text"""
        match = re.search(r'\d+', text)
        return int(match.group()) if match else None

    def _make_response(self, response_en: str, response_hi: str = None,
                       success: bool = True, action: str = None) -> dict:
        """Helper to create standardized response dict"""
        result = {
            'success': success,
            'response': response_en,
            'response_hi': response_hi or response_en,
        }
        if action:
            result['action'] = action
        return result
