"""
ARIA — Media Control Skill
Music, video, volume through keyboard media keys and app launching
"""

import subprocess
import logging
import os

logger = logging.getLogger(__name__)

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False


class MediaControl:
    """Media playback control commands"""

    MEDIA_APPS = {
        'spotify': ['spotify.exe', r'%APPDATA%\Spotify\Spotify.exe'],
        'vlc': ['vlc.exe', r'C:\Program Files\VideoLAN\VLC\vlc.exe',
                r'C:\Program Files (x86)\VideoLAN\VLC\vlc.exe'],
        'groove': 'mswindowsmusic:',
        'media player': 'wmplayer.exe',
        'windows media player': 'wmplayer.exe',
        'netflix': 'ms-windows-store://pdp/?ProductId=9WZDNCRFJ3PT',
        'youtube music': 'https://music.youtube.com',
        'gaana': 'https://gaana.com',
        'saavn': 'https://www.jiosaavn.com',
        'wynk': 'https://wynk.in',
    }

    def __init__(self, config: dict):
        self.config = config
        logger.info("MediaControl initialized")

    def _press_media_key(self, key: str) -> bool:
        """Press a media key using pyautogui"""
        if PYAUTOGUI_AVAILABLE:
            try:
                pyautogui.press(key)
                return True
            except Exception as e:
                logger.error(f"Media key error: {e}")
        return False

    def play_pause(self) -> dict:
        """Toggle play/pause"""
        if self._press_media_key('playpause'):
            return {'success': True, 'response': "Play/Pause toggled",
                    'response_hi': "Play/Pause टॉगल किया"}
        return {'success': False, 'response': "Could not control media"}

    def next_track(self) -> dict:
        """Skip to next track"""
        if self._press_media_key('nexttrack'):
            return {'success': True, 'response': "Skipped to next track ⏭️",
                    'response_hi': "अगले गाने पर चले गए ⏭️"}
        return {'success': False, 'response': "Could not skip track"}

    def previous_track(self) -> dict:
        """Go to previous track"""
        if self._press_media_key('prevtrack'):
            return {'success': True, 'response': "Going to previous track ⏮️",
                    'response_hi': "पिछले गाने पर वापस गए ⏮️"}
        return {'success': False, 'response': "Could not go back"}

    def stop_media(self) -> dict:
        """Stop media playback"""
        if self._press_media_key('stop'):
            return {'success': True, 'response': "Media stopped ⏹️",
                    'response_hi': "मीडिया रोक दिया ⏹️"}
        return {'success': False, 'response': "Could not stop media"}

    def open_spotify(self) -> dict:
        """Open Spotify"""
        paths = self.MEDIA_APPS.get('spotify', [])
        for path in paths:
            expanded = os.path.expandvars(path)
            if os.path.exists(expanded):
                try:
                    subprocess.Popen([expanded])
                    return {'success': True, 'response': "Opening Spotify 🎵",
                            'response_hi': "Spotify खोल रहा हूँ 🎵"}
                except Exception:
                    pass

        try:
            subprocess.Popen('spotify.exe', shell=True,
                             creationflags=subprocess.CREATE_NO_WINDOW)
            return {'success': True, 'response': "Opening Spotify 🎵",
                    'response_hi': "Spotify खोल रहा हूँ 🎵"}
        except Exception:
            import webbrowser
            webbrowser.open('https://open.spotify.com')
            return {'success': True, 'response': "Opening Spotify in browser 🎵",
                    'response_hi': "ब्राउज़र में Spotify खोल रहा हूँ 🎵"}

    def open_vlc(self) -> dict:
        """Open VLC Media Player"""
        for path in self.MEDIA_APPS.get('vlc', []):
            expanded = os.path.expandvars(path)
            if os.path.exists(expanded):
                subprocess.Popen([expanded])
                return {'success': True, 'response': "Opening VLC Media Player 🎬",
                        'response_hi': "VLC Media Player खोल रहा हूँ 🎬"}
        try:
            subprocess.Popen('vlc.exe', shell=True,
                             creationflags=subprocess.CREATE_NO_WINDOW)
            return {'success': True, 'response': "Opening VLC 🎬",
                    'response_hi': "VLC खोल रहा हूँ 🎬"}
        except Exception:
            return {'success': False,
                    'response': "VLC not installed. Download from https://www.videolan.org/",
                    'response_hi': "VLC इंस्टॉल नहीं है।"}

    def open_youtube_music(self) -> dict:
        """Open YouTube Music in browser"""
        import webbrowser
        webbrowser.open('https://music.youtube.com')
        return {'success': True, 'response': "Opening YouTube Music 🎵",
                'response_hi': "YouTube Music खोल रहा हूँ 🎵"}

    def play_on_youtube(self, query: str) -> dict:
        """Search and open music on YouTube"""
        import urllib.parse
        import webbrowser
        encoded = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={encoded}"
        webbrowser.open(url)
        return {
            'success': True,
            'response': f"Searching YouTube for '{query}' 🎵",
            'response_hi': f"YouTube पर '{query}' खोज रहा हूँ 🎵"
        }

    def play_on_spotify_search(self, query: str) -> dict:
        """Search Spotify for music"""
        import urllib.parse
        import webbrowser
        encoded = urllib.parse.quote(query)
        url = f"https://open.spotify.com/search/{encoded}"
        webbrowser.open(url)
        return {
            'success': True,
            'response': f"Searching Spotify for '{query}'",
            'response_hi': f"Spotify पर '{query}' खोज रहा हूँ"
        }
