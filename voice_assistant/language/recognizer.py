"""
ARIA Voice Assistant — Speech Recognition Engine
Supports English (en-IN) and Hindi (hi-IN) via Google Speech Recognition
Falls back gracefully when PyAudio is not available.
"""

import logging
import threading
import json

logger = logging.getLogger(__name__)

# Try importing audio dependencies
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False
    logger.warning("SpeechRecognition not available")

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    logger.info("PyAudio not available — mic input will use browser Web Speech API")

try:
    from langdetect import detect as detect_lang
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False


class SpeechRecognizer:
    """
    Speech-to-Text engine supporting English and Hindi.
    Primary: Google Speech Recognition API
    Fallback: Browser Web Speech API (handled on frontend)
    """

    LOCALES = {
        'en': 'en-IN',
        'hi': 'hi-IN',
        'ms': 'ms-MY',
        'en-IN': 'en-IN',
        'hi-IN': 'hi-IN',
        'ms-MY': 'ms-MY',
    }

    def __init__(self, config: dict):
        self.config = config
        self.lang_config = config.get('language', {})
        self.default_lang = self.lang_config.get('default', 'en')
        self._recognizer = sr.Recognizer() if SR_AVAILABLE else None
        self._is_listening = False
        self._lock = threading.Lock()

        if self._recognizer:
            # Tune recognizer for better accuracy
            self._recognizer.energy_threshold = 300
            self._recognizer.dynamic_energy_threshold = True
            self._recognizer.pause_threshold = 0.8
            self._recognizer.phrase_threshold = 0.3
            logger.info("SpeechRecognizer initialized with Google STT")

    @property
    def available(self) -> bool:
        return SR_AVAILABLE and PYAUDIO_AVAILABLE

    def listen(self, language: str = None, timeout: int = 8, phrase_timeout: int = 5) -> dict:
        """
        Listen from microphone and return recognized text.
        Returns: {'text': str, 'language': str, 'confidence': float}
        """
        if not self.available:
            return {'text': '', 'language': language or self.default_lang,
                    'error': 'Microphone not available — use browser voice input'}

        lang = language or self.default_lang
        locale = self.LOCALES.get(lang, 'en-IN')

        with self._lock:
            if self._is_listening:
                return {'text': '', 'language': lang, 'error': 'Already listening'}
            self._is_listening = True

        try:
            with sr.Microphone() as source:
                logger.info(f"Adjusting for ambient noise... (locale: {locale})")
                self._recognizer.adjust_for_ambient_noise(source, duration=0.5)
                logger.info("Listening...")

                audio = self._recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_timeout
                )

            # Try primary locale
            try:
                text = self._recognizer.recognize_google(audio, language=locale)
                detected_lang = self._detect_language(text)
                return {
                    'text': text,
                    'language': detected_lang,
                    'confidence': 0.9,
                    'locale': locale
                }
            except sr.UnknownValueError:
                # Try alternate locales
                alt_locales = [l for l in ['en-IN', 'hi-IN', 'ms-MY'] if l != locale]
                for alt_locale in alt_locales:
                    alt_lang = 'en' if 'en' in alt_locale else ('hi' if 'hi' in alt_locale else 'ms')
                    try:
                        text = self._recognizer.recognize_google(audio, language=alt_locale)
                        return {
                            'text': text,
                            'language': alt_lang,
                            'confidence': 0.75,
                            'locale': alt_locale
                        }
                    except sr.UnknownValueError:
                        continue
                return {'text': '', 'language': lang, 'error': 'Could not understand audio'}

        except sr.WaitTimeoutError:
            return {'text': '', 'language': lang, 'error': 'Listening timed out'}
        except Exception as e:
            logger.error(f"Recognition error: {e}")
            return {'text': '', 'language': lang, 'error': str(e)}
        finally:
            self._is_listening = False

    def _detect_language(self, text: str) -> str:
        """Detect if text is Hindi or English"""
        if not text:
            return self.default_lang

        # Check for Devanagari script (Hindi)
        for char in text:
            if '\u0900' <= char <= '\u097F':
                return 'hi'

        # Use langdetect if available
        if LANGDETECT_AVAILABLE:
            try:
                detected = detect_lang(text)
                if detected in ('hi', 'mr', 'ne'):
                    return 'hi'
                elif detected in ('ms', 'id'):
                    return 'ms'
            except Exception:
                pass

        return 'en'

    def listen_async(self, callback, language: str = None):
        """Listen asynchronously, call callback with result"""
        def _worker():
            result = self.listen(language=language)
            callback(result)

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
        return thread

    @staticmethod
    def is_microphone_available() -> bool:
        """Check if a microphone is accessible"""
        if not PYAUDIO_AVAILABLE:
            return False
        try:
            p = pyaudio.PyAudio()
            count = p.get_device_count()
            p.terminate()
            return count > 0
        except Exception:
            return False
