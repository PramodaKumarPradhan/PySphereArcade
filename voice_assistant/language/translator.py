"""
ARIA Voice Assistant — Language Translator
Bridges Hindi ↔ English using googletrans + script detection
"""

import logging
import re

logger = logging.getLogger(__name__)

try:
    from googletrans import Translator
    GOOGLETRANS_AVAILABLE = True
    _translator = Translator()
except Exception:
    try:
        # googletrans-py (Python 3.12+ compatible)
        from googletrans import Translator
        GOOGLETRANS_AVAILABLE = True
        _translator = Translator()
    except Exception:
        GOOGLETRANS_AVAILABLE = False
        _translator = None
        logger.warning("googletrans not available — translation disabled")

try:
    from langdetect import detect as _langdetect
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

# Devanagari Unicode range
DEVANAGARI_RE = re.compile(r'[\u0900-\u097F]')


class LanguageTranslator:
    """
    Handles language detection and translation between English and Hindi.
    Uses script detection as primary method (fast, offline),
    falls back to langdetect, then googletrans for translation.
    """

    # Common Hindi→English keyword mappings for fast offline command routing
    HINDI_COMMAND_MAP = {
        # Greetings
        'नमस्ते': 'hello', 'नमस्कार': 'hello', 'हाय': 'hi',
        'शुभ प्रभात': 'good morning', 'शुभ रात्रि': 'good night',
        'धन्यवाद': 'thank you', 'अलविदा': 'goodbye', 'बाय': 'goodbye',

        # Time & Date
        'समय': 'time', 'समय बताओ': 'what time is it',
        'तारीख': 'date', 'आज की तारीख': 'today date',
        'कितने बजे हैं': 'what time is it', 'कितना बजा है': 'what time is it',

        # System Commands
        'वॉल्यूम बढ़ाओ': 'volume up', 'आवाज़ बढ़ाओ': 'volume up',
        'वॉल्यूम घटाओ': 'volume down', 'आवाज़ कम करो': 'volume down',
        'म्यूट करो': 'mute', 'शांत करो': 'mute',
        'स्क्रीनशॉट': 'screenshot', 'स्क्रीनशॉट लो': 'take screenshot',
        'बंद करो': 'shutdown', 'बंद कर दो': 'shutdown',
        'रीस्टार्ट करो': 'restart', 'पुनः आरंभ': 'restart',
        'लॉक करो': 'lock screen', 'स्क्रीन लॉक': 'lock screen',
        'नींद': 'sleep', 'स्लीप करो': 'sleep',

        # Apps
        'नोटपैड खोलो': 'open notepad', 'नोटपैड': 'open notepad',
        'कैलकुलेटर खोलो': 'open calculator', 'कैलकुलेटर': 'open calculator',
        'वर्ड खोलो': 'open word', 'एक्सेल खोलो': 'open excel',
        'पावरपॉइंट खोलो': 'open powerpoint',
        'ब्राउज़र खोलो': 'open browser', 'इंटरनेट खोलो': 'open browser',
        'यूट्यूब': 'open youtube', 'यूट्यूब खोलो': 'open youtube',
        'गूगल': 'open google', 'गूगल खोलो': 'open google',
        'कैमरा': 'open camera', 'फोटो': 'open camera',

        # Search
        'खोजो': 'search', 'ढूंढो': 'search', 'सर्च करो': 'search',
        'गूगल पर खोजो': 'google search',
        'यूट्यूब पर लगाओ': 'youtube search',
        'यूट्यूब पर खोजो': 'youtube search',
        'विकिपीडिया': 'wikipedia',

        # Media
        'गाना बजाओ': 'play music', 'संगीत चलाओ': 'play music',
        'रोको': 'pause', 'बंद करो': 'stop',
        'अगला गाना': 'next track', 'पिछला गाना': 'previous track',

        # Information
        'मौसम': 'weather', 'मौसम बताओ': 'weather',
        'खबर': 'news', 'समाचार': 'news',
        'चुटकुला': 'joke', 'जोक सुनाओ': 'tell joke',
        'हिसाब': 'calculate', 'गणना': 'calculate',
        'बैटरी': 'battery status', 'चार्ज': 'battery status',

        # File / Folder
        'डाउनलोड': 'open downloads', 'डाउनलोड फोल्डर': 'open downloads',
        'डॉक्यूमेंट': 'open documents', 'दस्तावेज़': 'open documents',
        'डेस्कटॉप खोलो': 'open desktop',

        # Communication
        'ईमेल खोलो': 'open email', 'जीमेल खोलो': 'open gmail',
        'व्हाट्सएप': 'open whatsapp',

        # Night / Home
        'नाइट मोड': 'night mode on', 'रात का मोड': 'night mode on',
        'डार्क मोड': 'dark mode',
        'याद दिलाओ': 'set reminder', 'रिमाइंडर': 'set reminder',

        # New Alexa/Google/Siri Commands
        'वाइफ़ाई चालू': 'wifi on', 'वाइफ़ाई बंद': 'wifi off',
        'ब्लूटूथ चालू': 'bluetooth on', 'ब्लूटूथ बंद': 'bluetooth off',
        'हवाई जहाज मोड': 'airplane mode', 'एरोप्लेन मोड': 'airplane mode',
        'सिक्का उछालो': 'flip a coin', 'सिक्का घुमाओ': 'flip a coin',
        'पासा फेंको': 'roll a die', 'पासा घुमाओ': 'roll a die',
        'तथ्य बताओ': 'tell me a fact', 'रोचक तथ्य': 'tell me a fact',
        'क्या बारिश होगी': 'will it rain', 'छाते की ज़रूरत': 'do i need an umbrella',
        'शेयर मूल्य': 'stock price', 'शेयर का दाम': 'stock price',
        'लाइट चालू': 'turn on lights', 'लाइट बंद': 'turn off lights',
        'पंखा चालू': 'turn on fan', 'पंखा बंद': 'turn off fan',
        'एसी चालू': 'turn on ac', 'एसी बंद': 'turn off ac',

        # Assistant
        'मदद': 'help', 'सहायता': 'help',
        'धन्यवाद': 'thank you',
        'हिंदी में बोलो': 'speak in hindi',
        'अंग्रेजी में बोलो': 'speak in english',
    }

    def __init__(self, config: dict):
        self.config = config
        self.lang_config = config.get('language', {})
        logger.info(
            f"LanguageTranslator ready | googletrans={GOOGLETRANS_AVAILABLE} | "
            f"langdetect={LANGDETECT_AVAILABLE}"
        )

    def detect_language(self, text: str) -> str:
        """
        Detect language of text. Returns 'hi' or 'en'.
        Uses Devanagari script check first (fastest), then langdetect.
        """
        if not text:
            return self.lang_config.get('default', 'en')

        # Check for Devanagari script (fastest, offline)
        if DEVANAGARI_RE.search(text):
            return 'hi'

        # Use langdetect
        if LANGDETECT_AVAILABLE:
            try:
                detected = _langdetect(text)
                if detected in ('hi', 'mr', 'ne', 'gu'):
                    return 'hi'
                elif detected in ('ms', 'id', 'jv', 'su'):
                    return 'ms'
            except Exception:
                pass

        return 'en'

    def translate(self, text: str, src: str = 'auto', dest: str = 'en') -> str:
        """
        Translate text from src language to dest language.
        Returns original text if translation fails.
        """
        if not text or src == dest:
            return text

        # Check offline map first (Hindi→English)
        if src == 'hi' and dest == 'en':
            for hindi, english in self.HINDI_COMMAND_MAP.items():
                if text.strip().lower() == hindi:
                    return english

        if not GOOGLETRANS_AVAILABLE or _translator is None:
            return text

        try:
            result = _translator.translate(text, src=src, dest=dest)
            return result.text
        except Exception as e:
            logger.warning(f"Translation failed: {e}")
            return text

    def hindi_to_english_command(self, text: str) -> str:
        """
        Convert Hindi voice command to English equivalent.
        Uses keyword matching in the HINDI_COMMAND_MAP, then falls back to translate().
        """
        text_lower = text.strip().lower()

        # Direct map lookup (partial match)
        for hindi_key, english_val in self.HINDI_COMMAND_MAP.items():
            if hindi_key in text_lower or text_lower in hindi_key:
                return english_val

        # Full translation fallback
        return self.translate(text, src='hi', dest='en')

    def get_response_in_language(self, english_response: str, language: str) -> str:
        """
        Return the response in the target language.
        If language is 'hi', translate the English response to Hindi.
        """
        if language == 'en' or not english_response:
            return english_response

        if language == 'hi':
            translated = self.translate(english_response, src='en', dest='hi')
            return translated

        if language == 'ms':
            translated = self.translate(english_response, src='en', dest='ms')
            return translated

        return english_response
