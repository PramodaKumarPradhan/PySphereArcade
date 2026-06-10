"""
ARIA Voice Assistant — Speech Synthesizer (TTS)
Primary: pyttsx3 (offline, fast, no extra deps needed)
Fallback: gTTS (Google, natural Hindi) + Windows Media Player / pygame-ce
"""

import logging
import threading
import os
import tempfile
import time
import subprocess

logger = logging.getLogger(__name__)

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logger.warning("pyttsx3 not available")

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    logger.warning("gTTS not available")

try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except Exception:
    PYGAME_AVAILABLE = False

# Windows-native audio fallback (no compilation needed)
WINPLAY_AVAILABLE = os.name == 'nt'


class SpeechSynthesizer:
    """
    Text-to-Speech engine.
    - English: pyttsx3 (offline, low latency)
    - Hindi: gTTS → pygame (natural voice)
    - Fallback: pyttsx3 for both if gTTS unavailable
    """

    GTTS_LOCALES = {'en': 'en', 'hi': 'hi', 'ms': 'ms'}
    PYTTSX3_RATE = {'en': 165, 'hi': 145, 'ms': 155}

    def __init__(self, config: dict):
        self.config = config
        self.voice_config = config.get('voice', {})
        self._lock = threading.Lock()
        self._is_speaking = False
        self._tts_engine = None
        self._temp_files = []

        # Initialize pyttsx3
        if PYTTSX3_AVAILABLE:
            self._init_pyttsx3()

        logger.info(
            f"SpeechSynthesizer ready | pyttsx3={PYTTSX3_AVAILABLE} | "
            f"gTTS={GTTS_AVAILABLE} | pygame={PYGAME_AVAILABLE} | winplay={WINPLAY_AVAILABLE}"
        )

    def _init_pyttsx3(self):
        """Initialize pyttsx3 engine with female voice if available"""
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            volume = self.voice_config.get('volume', 0.92)
            rate_en = self.voice_config.get('rate_en', 165)

            engine.setProperty('volume', volume)
            engine.setProperty('rate', rate_en)

            # Prefer female voice
            preferred_gender = self.voice_config.get('gender', 'female')
            for voice in voices:
                name_lower = voice.name.lower()
                if preferred_gender == 'female' and any(
                    kw in name_lower for kw in ('zira', 'hazel', 'female', 'heera', 'sapan')
                ):
                    engine.setProperty('voice', voice.id)
                    logger.info(f"Selected voice: {voice.name}")
                    break

            self._tts_engine = engine
        except Exception as e:
            logger.error(f"pyttsx3 init error: {e}")
            self._tts_engine = None

    def speak(self, text: str, language: str = 'en', blocking: bool = False):
        """
        Speak the given text in the specified language.
        language: 'en' or 'hi'
        """
        if not text or text.strip() == '':
            return

        # Clean text for TTS
        text = self._clean_for_tts(text, language)

        if blocking:
            self._speak_sync(text, language)
        else:
            thread = threading.Thread(
                target=self._speak_sync,
                args=(text, language),
                daemon=True
            )
            thread.start()

    def _speak_sync(self, text: str, language: str):
        """Synchronously speak text"""
        with self._lock:
            self._is_speaking = True
            try:
                if language == 'hi' and GTTS_AVAILABLE:
                    self._speak_gtts(text, language)
                elif self._tts_engine and PYTTSX3_AVAILABLE:
                    self._speak_pyttsx3(text, language)
                elif GTTS_AVAILABLE:
                    self._speak_gtts(text, language)
                else:
                    logger.warning(f"No TTS engine available to speak: {text}")
            except Exception as e:
                logger.error(f"TTS error: {e}")
            finally:
                self._is_speaking = False

    def _speak_pyttsx3(self, text: str, language: str):
        """Speak using pyttsx3"""
        try:
            rate = self.PYTTSX3_RATE.get(language, 165)
            self._tts_engine.setProperty('rate', rate)
            self._tts_engine.say(text)
            self._tts_engine.runAndWait()
        except Exception as e:
            logger.error(f"pyttsx3 speak error: {e}")

    def _speak_gtts(self, text: str, language: str):
        """Speak using Google TTS, play with pygame or Windows Media Player"""
        try:
            locale = self.GTTS_LOCALES.get(language, 'en')
            tts = gTTS(text=text, lang=locale, slow=False)

            # Save to temp file
            tmp = tempfile.NamedTemporaryFile(
                suffix='.mp3', delete=False,
                dir=tempfile.gettempdir(), prefix='aria_'
            )
            tmp_path = tmp.name
            tmp.close()
            tts.save(tmp_path)
            self._temp_files.append(tmp_path)

            played = False

            # Try pygame first
            if PYGAME_AVAILABLE:
                try:
                    pygame.mixer.music.load(tmp_path)
                    pygame.mixer.music.set_volume(self.voice_config.get('volume', 0.92))
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.05)
                    pygame.mixer.music.unload()
                    played = True
                except Exception:
                    pass

            # Fallback: Windows Media Player (silent playback)
            if not played and WINPLAY_AVAILABLE:
                try:
                    proc = subprocess.Popen(
                        ['powershell', '-c',
                         f'(New-Object Media.SoundPlayer "{tmp_path}").PlaySync()'],
                        creationflags=subprocess.CREATE_NO_WINDOW,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )
                    proc.wait(timeout=30)
                    played = True
                except Exception:
                    pass

            # Fallback 2: Windows built-in wmplayer
            if not played and WINPLAY_AVAILABLE:
                try:
                    proc = subprocess.Popen(
                        f'start /wait wmplayer /play /close "{tmp_path}"',
                        shell=True, creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    proc.wait(timeout=30)
                    played = True
                except Exception:
                    pass

            self._cleanup_temp(tmp_path)

        except Exception as e:
            logger.error(f"gTTS speak error: {e}")
            # Fallback to pyttsx3
            if self._tts_engine:
                self._speak_pyttsx3(text, language)

    def _cleanup_temp(self, path: str):
        """Remove a temp file"""
        try:
            if os.path.exists(path):
                os.remove(path)
            if path in self._temp_files:
                self._temp_files.remove(path)
        except Exception:
            pass

    def _clean_for_tts(self, text: str, language: str) -> str:
        """Remove markdown, URLs, and special chars that TTS doesn't handle well"""
        import re
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        # Remove markdown bold/italic
        text = re.sub(r'\*+', '', text)
        text = re.sub(r'_+', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text.strip()

    def stop(self):
        """Stop current speech"""
        try:
            if PYGAME_AVAILABLE:
                pygame.mixer.music.stop()
        except Exception:
            pass
        try:
            if self._tts_engine:
                self._tts_engine.stop()
        except Exception:
            pass
        self._is_speaking = False

    @property
    def is_speaking(self) -> bool:
        return self._is_speaking

    def set_rate(self, rate: int, language: str = 'en'):
        """Adjust speech rate"""
        self.PYTTSX3_RATE[language] = max(80, min(300, rate))
        if self._tts_engine:
            try:
                self._tts_engine.setProperty('rate', self.PYTTSX3_RATE[language])
            except Exception:
                pass

    def set_volume(self, volume: float):
        """Set volume 0.0-1.0"""
        self.voice_config['volume'] = max(0.0, min(1.0, volume))
        if self._tts_engine:
            try:
                self._tts_engine.setProperty('volume', volume)
            except Exception:
                pass
