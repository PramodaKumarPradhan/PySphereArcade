"""
ARIA — PC Automation Skill (Enhanced)
Deep Windows integration:
  - Open ANY installed application (registry scan + Start Menu search)
  - Open ANY website by name or URL
  - Type/dictate text into any open window
  - Create files with content (Notepad, Word, text files)
  - Window management: switch, resize, focus
  - Clipboard operations
  - Run system commands
  - Write & create documents by voice
"""

import os
import re
import time
import logging
import subprocess
import threading
import winreg
import glob
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import pyautogui
    pyautogui.FAILSAFE = False
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


# ── Known Website Mappings ───────────────────────────────────────────────────

WEBSITE_MAP = {
    # Search & Productivity
    'google': 'https://www.google.com',
    'gmail': 'https://mail.google.com',
    'google drive': 'https://drive.google.com',
    'google docs': 'https://docs.google.com',
    'google sheets': 'https://sheets.google.com',
    'google slides': 'https://slides.google.com',
    'google meet': 'https://meet.google.com',
    'google calendar': 'https://calendar.google.com',
    'google maps': 'https://maps.google.com',
    'google translate': 'https://translate.google.com',
    'google photos': 'https://photos.google.com',
    'google classroom': 'https://classroom.google.com',

    # Microsoft
    'outlook': 'https://outlook.live.com',
    'outlook mail': 'https://outlook.live.com/mail',
    'hotmail': 'https://outlook.live.com',
    'onedrive': 'https://onedrive.live.com',
    'office online': 'https://office.live.com',
    'microsoft teams online': 'https://teams.microsoft.com',
    'bing': 'https://www.bing.com',
    'msn': 'https://www.msn.com',
    'azure': 'https://portal.azure.com',
    'github': 'https://github.com',
    'linkedin': 'https://www.linkedin.com',

    # Video & Entertainment
    'youtube': 'https://www.youtube.com',
    'youtube music': 'https://music.youtube.com',
    'netflix': 'https://www.netflix.com',
    'amazon prime': 'https://www.primevideo.com',
    'prime video': 'https://www.primevideo.com',
    'hotstar': 'https://www.hotstar.com',
    'disney plus': 'https://www.disneyplus.com',
    'twitch': 'https://www.twitch.tv',
    'vimeo': 'https://www.vimeo.com',

    # Social Media
    'facebook': 'https://www.facebook.com',
    'instagram': 'https://www.instagram.com',
    'twitter': 'https://www.twitter.com',
    'x': 'https://www.x.com',
    'reddit': 'https://www.reddit.com',
    'whatsapp web': 'https://web.whatsapp.com',
    'whatsapp': 'https://web.whatsapp.com',
    'telegram web': 'https://web.telegram.org',
    'snapchat': 'https://www.snapchat.com',
    'pinterest': 'https://www.pinterest.com',

    # News & Info
    'bbc': 'https://www.bbc.com',
    'bbc news': 'https://www.bbc.com/news',
    'cnn': 'https://www.cnn.com',
    'ndtv': 'https://www.ndtv.com',
    'times of india': 'https://timesofindia.indiatimes.com',
    'hindustan times': 'https://www.hindustantimes.com',
    'wikipedia': 'https://www.wikipedia.org',
    'quora': 'https://www.quora.com',
    'medium': 'https://www.medium.com',
    'stack overflow': 'https://stackoverflow.com',

    # Shopping
    'amazon': 'https://www.amazon.in',
    'flipkart': 'https://www.flipkart.com',
    'myntra': 'https://www.myntra.com',
    'ebay': 'https://www.ebay.com',
    'meesho': 'https://www.meesho.com',

    # Developer Tools
    'chatgpt': 'https://chat.openai.com',
    'claude': 'https://claude.ai',
    'gemini': 'https://gemini.google.com',
    'copilot': 'https://copilot.microsoft.com',
    'perplexity': 'https://www.perplexity.ai',
    'stackoverflow': 'https://stackoverflow.com',
    'codepen': 'https://codepen.io',
    'replit': 'https://replit.com',
    'vercel': 'https://vercel.com',

    # Communication
    'zoom': 'https://zoom.us',
    'discord': 'https://discord.com/app',
    'slack': 'https://slack.com',

    # Finance
    'zerodha': 'https://zerodha.com',
    'groww': 'https://groww.in',
    'moneycontrol': 'https://www.moneycontrol.com',
    'paytm': 'https://www.paytm.com',
    'phonepe': 'https://www.phonepe.com',

    # Utility
    'speedtest': 'https://www.speedtest.net',
    'canva': 'https://www.canva.com',
    'figma': 'https://www.figma.com',
    'trello': 'https://trello.com',
    'notion': 'https://www.notion.so',
    'dropbox': 'https://www.dropbox.com',
    'ilovepdf': 'https://www.ilovepdf.com',
    'smallpdf': 'https://smallpdf.com',
}

# ── Known App EXE Mappings ───────────────────────────────────────────────────

APP_MAP = {
    # Windows Built-in
    'notepad': 'notepad.exe',
    'calculator': 'calc.exe',
    'paint': 'mspaint.exe',
    'wordpad': 'wordpad.exe',
    'snipping tool': 'SnippingTool.exe',
    'snip': 'SnippingTool.exe',
    'sticky notes': 'stikynot.exe',
    'task manager': 'taskmgr.exe',
    'device manager': 'devmgmt.msc',
    'control panel': 'control.exe',
    'settings': 'ms-settings:',
    'windows settings': 'ms-settings:',
    'registry': 'regedit.exe',
    'cmd': 'cmd.exe',
    'command prompt': 'cmd.exe',
    'powershell': 'powershell.exe',
    'file explorer': 'explorer.exe',
    'explorer': 'explorer.exe',
    'this pc': 'explorer.exe',
    'my computer': 'explorer.exe',
    'character map': 'charmap.exe',
    'magnifier': 'magnify.exe',
    'narrator': 'narrator.exe',
    'onscreen keyboard': 'osk.exe',
    'remote desktop': 'mstsc.exe',
    'disk cleanup': 'cleanmgr.exe',
    'defragment': 'dfrgui.exe',
    'resource monitor': 'resmon.exe',
    'performance monitor': 'perfmon.exe',
    'event viewer': 'eventvwr.msc',
    'services': 'services.msc',
    'msconfig': 'msconfig.exe',

    # Microsoft Office
    'word': 'WINWORD.EXE',
    'microsoft word': 'WINWORD.EXE',
    'excel': 'EXCEL.EXE',
    'microsoft excel': 'EXCEL.EXE',
    'powerpoint': 'POWERPNT.EXE',
    'microsoft powerpoint': 'POWERPNT.EXE',
    'outlook': 'OUTLOOK.EXE',
    'microsoft outlook': 'OUTLOOK.EXE',
    'teams': 'teams.exe',
    'microsoft teams': 'teams.exe',
    'onenote': 'ONENOTE.EXE',
    'access': 'MSACCESS.EXE',
    'publisher': 'MSPUB.EXE',
    'visio': 'VISIO.EXE',

    # Browsers
    'chrome': 'chrome.exe',
    'google chrome': 'chrome.exe',
    'firefox': 'firefox.exe',
    'mozilla firefox': 'firefox.exe',
    'edge': 'msedge.exe',
    'microsoft edge': 'msedge.exe',
    'brave': 'brave.exe',
    'opera': 'opera.exe',
    'internet explorer': 'iexplore.exe',

    # Media Players
    'vlc': 'vlc.exe',
    'vlc media player': 'vlc.exe',
    'windows media player': 'wmplayer.exe',
    'media player': 'wmplayer.exe',
    'groove music': 'mswindowsmusic:',
    'spotify': 'spotify.exe',

    # Communication
    'whatsapp': 'whatsapp.exe',
    'telegram': 'telegram.exe',
    'zoom': 'zoom.exe',
    'skype': 'skype.exe',
    'discord': 'discord.exe',
    'slack': 'slack.exe',
    'signal': 'signal.exe',

    # Development
    'visual studio code': 'code.exe',
    'vscode': 'code.exe',
    'vs code': 'code.exe',
    'visual studio': 'devenv.exe',
    'pycharm': 'pycharm64.exe',
    'android studio': 'studio64.exe',
    'eclipse': 'eclipse.exe',
    'sublime text': 'sublime_text.exe',
    'atom': 'atom.exe',
    'notepad++': 'notepad++.exe',
    'git bash': 'git-bash.exe',
    'github desktop': 'GitHubDesktop.exe',
    'postman': 'postman.exe',
    'docker': 'Docker Desktop.exe',

    # Creative
    'photoshop': 'Photoshop.exe',
    'illustrator': 'Illustrator.exe',
    'premiere': 'Adobe Premiere Pro.exe',
    'after effects': 'AfterFX.exe',
    'lightroom': 'lightroom.exe',
    'audacity': 'audacity.exe',
    'obs': 'obs64.exe',
    'obs studio': 'obs64.exe',
    'blender': 'blender.exe',
    'gimp': 'gimp-2.10.exe',
    'inkscape': 'inkscape.exe',

    # Productivity
    'notion': 'notion.exe',
    'todoist': 'todoist.exe',
    'obsidian': 'Obsidian.exe',
    'trello': 'trello.exe',
    'evernote': 'evernote.exe',

    # Utilities
    '7zip': '7zfm.exe',
    '7-zip': '7zfm.exe',
    'winrar': 'winrar.exe',
    'winzip': 'winzip32.exe',
    'ccleaner': 'CCleaner64.exe',
    'virtualbox': 'virtualbox.exe',
    'vmware': 'vmware.exe',
    'putty': 'putty.exe',
    'winscp': 'WinSCP.exe',
    'filezilla': 'filezilla.exe',

    # Games
    'steam': 'steam.exe',
    'epic games': 'EpicGamesLauncher.exe',
    'minecraft': 'javaw.exe',

    # System
    'camera': 'microsoft.windows.camera:',
    'photos': 'ms-photos:',
    'store': 'ms-windows-store:',
    'xbox': 'ms-xbox:',
    'maps': 'bingmaps:',
    'mail': 'outlookmail:',
    'clock': 'ms-clock:',
    'weather': 'bingweather:',
    'calendar': 'outlookcal:',
    'news': 'bingnews:',
    'paint 3d': 'ms-paint:',
    'video editor': 'ms-photos:filmstrip',
}


class PcAutomation:
    """
    Full PC automation: open apps, websites, type text, create files,
    manage windows, run commands.
    """

    def __init__(self, config: dict):
        self.config = config
        self._installed_apps_cache = {}
        self._cache_lock = threading.Lock()
        self._typing_mode = False
        self._typing_target = None

        # Build app cache in background
        threading.Thread(target=self._build_app_cache, daemon=True).start()
        logger.info("PcAutomation initialized")

    # ═══════════════════════════════════════════════════════════════
    # OPEN WEBSITE
    # ═══════════════════════════════════════════════════════════════

    def open_website(self, site: str) -> dict:
        """Open a website by name or URL in default browser"""
        import webbrowser
        site_clean = site.strip().lower()

        # Direct URL match
        if site_clean in WEBSITE_MAP:
            url = WEBSITE_MAP[site_clean]
            webbrowser.open(url)
            return {
                'success': True,
                'response': f"Opening {site} in your browser.",
                'response_hi': f"{site} ब्राउज़र में खोल रहा हूँ।"
            }

        # Partial match
        for key, url in WEBSITE_MAP.items():
            if key in site_clean or site_clean in key:
                webbrowser.open(url)
                return {
                    'success': True,
                    'response': f"Opening {key} in your browser.",
                    'response_hi': f"{key} खोल रहा हूँ।"
                }

        # Raw URL (if it has a dot)
        if '.' in site_clean and not ' ' in site_clean:
            url = site_clean if site_clean.startswith('http') else f'https://{site_clean}'
            webbrowser.open(url)
            return {
                'success': True,
                'response': f"Opening {url}",
                'response_hi': f"{url} खोल रहा हूँ।"
            }

        # Google search fallback
        query = site.replace(' ', '+')
        webbrowser.open(f'https://www.google.com/search?q={query}')
        return {
            'success': True,
            'response': f"Searching Google for '{site}'",
            'response_hi': f"Google पर '{site}' खोज रहा हूँ।"
        }

    def open_website_with_search(self, site: str, query: str = '') -> dict:
        """Open a website and optionally search within it"""
        import webbrowser
        site_clean = site.lower().strip()
        url = WEBSITE_MAP.get(site_clean, f'https://{site_clean}')

        if query:
            search_patterns = {
                'youtube.com': f'https://www.youtube.com/results?search_query={query.replace(" ", "+")}',
                'google.com': f'https://www.google.com/search?q={query.replace(" ", "+")}',
                'amazon.in': f'https://www.amazon.in/s?k={query.replace(" ", "+")}',
                'flipkart.com': f'https://www.flipkart.com/search?q={query.replace(" ", "+")}',
                'wikipedia.org': f'https://en.wikipedia.org/wiki/Special:Search?search={query.replace(" ", "_")}',
                'twitter.com': f'https://twitter.com/search?q={query.replace(" ", "+")}',
                'x.com': f'https://x.com/search?q={query.replace(" ", "+")}',
                'github.com': f'https://github.com/search?q={query.replace(" ", "+")}',
                'stackoverflow.com': f'https://stackoverflow.com/search?q={query.replace(" ", "+")}',
            }
            for domain, search_url in search_patterns.items():
                if domain in url:
                    webbrowser.open(search_url)
                    return {
                        'success': True,
                        'response': f"Searching '{query}' on {site}",
                        'response_hi': f"{site} पर '{query}' खोज रहा हूँ।"
                    }

        webbrowser.open(url)
        return {
            'success': True,
            'response': f"Opening {site}",
            'response_hi': f"{site} खोल रहा हूँ।"
        }

    # ═══════════════════════════════════════════════════════════════
    # OPEN APPLICATION (with registry scanning)
    # ═══════════════════════════════════════════════════════════════

    def open_application(self, app_name: str) -> dict:
        """Smart app opener: checks known map, registry, Start Menu, PATH"""
        name_lower = app_name.strip().lower()

        # 1. Check website map first for web apps
        if name_lower in WEBSITE_MAP:
            return self.open_website(name_lower)

        # 2. Check known app map
        if name_lower in APP_MAP:
            exe = APP_MAP[name_lower]
            return self._launch_exe(exe, app_name)

        # 3. Partial match in known map
        for key, exe in APP_MAP.items():
            if name_lower in key or key in name_lower:
                return self._launch_exe(exe, key)

        # 4. Check cached installed apps (from registry scan)
        cached = self._find_in_cache(name_lower)
        if cached:
            return self._launch_exe(cached, app_name)

        # 5. Try Start Menu / All Programs search
        start_menu_result = self._search_start_menu(name_lower)
        if start_menu_result:
            return self._launch_exe(start_menu_result, app_name)

        # 6. Search PATH
        found = shutil.which(app_name) or shutil.which(f'{app_name}.exe')
        if found:
            return self._launch_exe(found, app_name)

        # 7. Try direct execution anyway
        try:
            subprocess.Popen(app_name, shell=True,
                             creationflags=subprocess.CREATE_NO_WINDOW)
            return {
                'success': True,
                'response': f"Trying to open {app_name}...",
                'response_hi': f"{app_name} खोलने की कोशिश कर रहा हूँ..."
            }
        except Exception:
            pass

        return {
            'success': False,
            'response': f"I couldn't find '{app_name}' installed on your PC. Please check the name.",
            'response_hi': f"'{app_name}' नहीं मिला। कृपया नाम जांचें।"
        }

    def _launch_exe(self, exe: str, display_name: str) -> dict:
        """Launch an executable or URI"""
        try:
            if (exe.startswith('ms-') or exe.startswith('microsoft.')
                    or exe.startswith('outlook') or exe.startswith('bing')
                    or exe.endswith(':') or 'shell:' in exe):
                os.startfile(exe)
            elif exe.endswith('.msc'):
                subprocess.Popen(['mmc', exe], shell=False,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            elif exe.endswith('.lnk') or exe.endswith('.url'):
                os.startfile(exe)
            else:
                subprocess.Popen(exe, shell=True,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            time.sleep(0.5)
            return {
                'success': True,
                'response': f"Opening {display_name}.",
                'response_hi': f"{display_name} खोल रहा हूँ।"
            }
        except Exception as e:
            logger.error(f"Launch error for {exe}: {e}")
            return {
                'success': False,
                'response': f"Could not open {display_name}: {str(e)[:60]}",
                'response_hi': f"{display_name} नहीं खुला।"
            }

    def _build_app_cache(self):
        """Scan Windows registry & Start Menu to find installed apps"""
        cache = {}
        registry_keys = [
            (winreg.HKEY_LOCAL_MACHINE,
             r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall'),
            (winreg.HKEY_LOCAL_MACHINE,
             r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall'),
            (winreg.HKEY_CURRENT_USER,
             r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall'),
        ]
        for hive, key_path in registry_keys:
            try:
                with winreg.OpenKey(hive, key_path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                try:
                                    display_name = winreg.QueryValueEx(subkey, 'DisplayName')[0]
                                    install_loc = winreg.QueryValueEx(subkey, 'InstallLocation')[0]
                                    if display_name and install_loc:
                                        dn_lower = display_name.lower().strip()
                                        # Find the main exe in the install dir
                                        exe_path = self._find_main_exe(install_loc, display_name)
                                        if exe_path:
                                            cache[dn_lower] = exe_path
                                except (FileNotFoundError, OSError):
                                    pass
                        except OSError:
                            pass
            except Exception:
                pass

        # Also scan Start Menu shortcuts
        start_menu_paths = [
            os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Start Menu\Programs'),
            r'C:\ProgramData\Microsoft\Windows\Start Menu\Programs',
        ]
        for sm_path in start_menu_paths:
            for lnk in glob.glob(os.path.join(sm_path, '**', '*.lnk'), recursive=True):
                try:
                    name = os.path.splitext(os.path.basename(lnk))[0].lower()
                    cache[name] = lnk
                except Exception:
                    pass

        with self._cache_lock:
            self._installed_apps_cache = cache
        logger.info(f"App cache built: {len(cache)} apps found")

    def _find_main_exe(self, install_dir: str, app_name: str) -> str:
        """Find the main executable in an install directory"""
        if not install_dir or not os.path.isdir(install_dir):
            return None
        # Prefer exe that matches app name
        name_parts = app_name.lower().split()[:2]
        try:
            for exe in glob.glob(os.path.join(install_dir, '*.exe')):
                base = os.path.basename(exe).lower()
                if any(p in base for p in name_parts):
                    return exe
            # Return first exe
            exes = glob.glob(os.path.join(install_dir, '*.exe'))
            if exes:
                return exes[0]
        except Exception:
            pass
        return None

    def _find_in_cache(self, name: str) -> str:
        """Find closest match in installed apps cache"""
        with self._cache_lock:
            if name in self._installed_apps_cache:
                return self._installed_apps_cache[name]
            # Partial match
            for cached_name, path in self._installed_apps_cache.items():
                if name in cached_name or cached_name.startswith(name[:4]):
                    return path
        return None

    def _search_start_menu(self, name: str) -> str:
        """Search Start Menu for app shortcuts"""
        paths = [
            os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Start Menu\Programs'),
            r'C:\ProgramData\Microsoft\Windows\Start Menu\Programs',
        ]
        for sm_path in paths:
            for f in glob.glob(os.path.join(sm_path, '**', f'*{name}*.lnk'), recursive=True):
                return f
            for f in glob.glob(os.path.join(sm_path, '**', f'*{name}*.exe'), recursive=True):
                return f
        return None

    def list_installed_apps(self) -> dict:
        """List installed apps from cache"""
        with self._cache_lock:
            apps = sorted(self._installed_apps_cache.keys())[:30]
        if not apps:
            apps = list(APP_MAP.keys())[:20]
        return {
            'success': True,
            'response': f"I found {len(apps)} apps. Some include: {', '.join(apps[:10])}.",
            'response_hi': f"मुझे {len(apps)} ऐप्स मिले। जैसे: {', '.join(apps[:8])}।",
            'apps': apps
        }

    # ═══════════════════════════════════════════════════════════════
    # TYPE / WRITE IN ACTIVE WINDOW
    # ═══════════════════════════════════════════════════════════════

    def type_text(self, text: str, app_name: str = None) -> dict:
        """
        Type text into the current focused window (or a named app).
        Supports: notepad, word, any text editor.
        """
        if not PYAUTOGUI_AVAILABLE:
            return {
                'success': False,
                'response': "Typing not available (pyautogui not installed)",
                'response_hi': "टाइपिंग उपलब्ध नहीं है।"
            }

        try:
            # If app is specified, bring it to focus
            if app_name:
                self._focus_window(app_name)
                time.sleep(0.8)

            # Click in the window to ensure focus
            pyautogui.click()
            time.sleep(0.3)

            # Use clipboard for reliable typing (handles all Unicode including Hindi)
            if CLIPBOARD_AVAILABLE:
                old_clipboard = ''
                try:
                    old_clipboard = pyperclip.paste()
                except Exception:
                    pass
                pyperclip.copy(text)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.2)
                # Restore clipboard
                try:
                    pyperclip.copy(old_clipboard)
                except Exception:
                    pass
            else:
                # Direct typing (may not handle special chars well)
                pyautogui.typewrite(text, interval=0.05)

            return {
                'success': True,
                'response': f"Typed: \"{text[:60]}{'...' if len(text) > 60 else ''}\"",
                'response_hi': f"टाइप किया: \"{text[:40]}{'...' if len(text) > 40 else ''}\""
            }
        except Exception as e:
            logger.error(f"Type text error: {e}")
            return {
                'success': False,
                'response': f"Could not type text: {e}",
                'response_hi': "टेक्स्ट टाइप नहीं हो सका।"
            }

    def _focus_window(self, app_name: str):
        """Bring an app window to foreground using Alt+Tab cycling or tasklist"""
        try:
            import ctypes
            # Try using Windows API to find and focus window
            app_lower = app_name.lower()

            # Common window title patterns
            window_titles = {
                'notepad': 'Notepad',
                'word': 'Microsoft Word',
                'excel': 'Microsoft Excel',
                'powerpoint': 'Microsoft PowerPoint',
                'chrome': 'Google Chrome',
                'edge': 'Microsoft Edge',
                'firefox': 'Mozilla Firefox',
                'calculator': 'Calculator',
                'paint': 'Paint',
            }

            title_hint = window_titles.get(app_lower, app_name)

            # Use PowerShell to bring window to front
            ps_cmd = f'''
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {{
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);
}}
"@
$hwnd = [Win32]::FindWindow($null, "{title_hint}")
if ($hwnd -ne [IntPtr]::Zero) {{ [Win32]::SetForegroundWindow($hwnd) | Out-Null }}
'''
            subprocess.run(
                ['powershell', '-NonInteractive', '-Command', ps_cmd],
                capture_output=True, timeout=3,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except Exception:
            pass

    # ═══════════════════════════════════════════════════════════════
    # OPEN APP AND WRITE CONTENT
    # ═══════════════════════════════════════════════════════════════

    def open_and_write(self, app: str, content: str) -> dict:
        """Open an application and write content into it"""
        # Open the app
        result = self.open_application(app)
        if not result['success']:
            return result

        # Wait for it to open
        time.sleep(2.5)

        # Type the content
        return self.type_text(content, app)

    def open_notepad_and_write(self, content: str) -> dict:
        """Open Notepad and type content"""
        # Open notepad
        subprocess.Popen('notepad.exe', shell=True,
                         creationflags=subprocess.CREATE_NO_WINDOW)
        time.sleep(2.0)

        if not PYAUTOGUI_AVAILABLE:
            return {
                'success': False,
                'response': "Notepad opened but can't type (pyautogui missing)",
                'response_hi': "Notepad खुला पर टाइप नहीं हो सका।"
            }

        try:
            # Focus Notepad window
            self._focus_window('notepad')
            time.sleep(0.5)
            pyautogui.click()
            time.sleep(0.3)

            # Type content via clipboard
            if CLIPBOARD_AVAILABLE:
                pyperclip.copy(content)
                pyautogui.hotkey('ctrl', 'v')
            else:
                pyautogui.typewrite(content, interval=0.04)

            return {
                'success': True,
                'response': f"Opened Notepad and wrote: \"{content[:80]}\"",
                'response_hi': f"Notepad खोला और लिखा: \"{content[:60]}\""
            }
        except Exception as e:
            return {
                'success': False,
                'response': f"Notepad opened but writing failed: {e}",
                'response_hi': "Notepad खुला पर लिखने में त्रुटि हुई।"
            }

    def create_and_save_file(self, filename: str, content: str,
                             location: str = 'desktop') -> dict:
        """Create a file with content and save it"""
        try:
            # Resolve save location
            locations = {
                'desktop': os.path.expandvars('%USERPROFILE%\\Desktop'),
                'documents': os.path.expandvars('%USERPROFILE%\\Documents'),
                'downloads': os.path.expandvars('%USERPROFILE%\\Downloads'),
                'temp': os.path.expandvars('%TEMP%'),
            }
            save_dir = locations.get(location.lower(),
                                     os.path.expandvars('%USERPROFILE%\\Desktop'))
            os.makedirs(save_dir, exist_ok=True)

            # Add extension if not present
            if not os.path.splitext(filename)[1]:
                filename += '.txt'

            filepath = os.path.join(save_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                'success': True,
                'response': f"File '{filename}' created and saved to {location} with your content.",
                'response_hi': f"फ़ाइल '{filename}' {location} में सेव हो गई।",
                'filepath': filepath
            }
        except Exception as e:
            return {
                'success': False,
                'response': f"Could not create file: {e}",
                'response_hi': "फ़ाइल नहीं बन सकी।"
            }

    def open_file_in_notepad(self, filepath: str) -> dict:
        """Open a specific file in Notepad"""
        try:
            subprocess.Popen(f'notepad.exe "{filepath}"', shell=True,
                             creationflags=subprocess.CREATE_NO_WINDOW)
            return {
                'success': True,
                'response': f"Opened {os.path.basename(filepath)} in Notepad.",
                'response_hi': f"Notepad में {os.path.basename(filepath)} खोला।"
            }
        except Exception as e:
            return {'success': False, 'response': f"Could not open file: {e}"}

    # ═══════════════════════════════════════════════════════════════
    # WINDOW MANAGEMENT
    # ═══════════════════════════════════════════════════════════════

    def switch_window(self) -> dict:
        """Alt+Tab to switch windows"""
        if PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey('alt', 'tab')
            return {
                'success': True,
                'response': "Switched to previous window.",
                'response_hi': "पिछली विंडो पर गए।"
            }
        return {'success': False, 'response': "Not available"}

    def minimize_window(self) -> dict:
        """Minimize current window"""
        if PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey('win', 'down')
            return {
                'success': True,
                'response': "Window minimized.",
                'response_hi': "विंडो छोटी की।"
            }
        return {'success': False, 'response': "Not available"}

    def maximize_window(self) -> dict:
        """Maximize current window"""
        if PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey('win', 'up')
            return {
                'success': True,
                'response': "Window maximized.",
                'response_hi': "विंडो बड़ी की।"
            }
        return {'success': False, 'response': "Not available"}

    def close_window(self) -> dict:
        """Close current window with Alt+F4"""
        if PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey('alt', 'f4')
            return {
                'success': True,
                'response': "Window closed.",
                'response_hi': "विंडो बंद की।"
            }
        return {'success': False, 'response': "Not available"}

    def snap_left(self) -> dict:
        """Snap window to left half"""
        if PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey('win', 'left')
            return {'success': True, 'response': "Window snapped left.",
                    'response_hi': "विंडो बाईं तरफ लगाई।"}
        return {'success': False, 'response': "Not available"}

    def snap_right(self) -> dict:
        """Snap window to right half"""
        if PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey('win', 'right')
            return {'success': True, 'response': "Window snapped right.",
                    'response_hi': "विंडो दाईं तरफ लगाई।"}
        return {'success': False, 'response': "Not available"}

    def new_virtual_desktop(self) -> dict:
        """Create a new virtual desktop"""
        if PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey('win', 'ctrl', 'd')
            return {'success': True, 'response': "New virtual desktop created.",
                    'response_hi': "नया वर्चुअल डेस्कटॉप बनाया।"}
        return {'success': False, 'response': "Not available"}

    def open_run_dialog(self, command: str = '') -> dict:
        """Open Run dialog and execute command"""
        if PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey('win', 'r')
            time.sleep(0.5)
            if command:
                pyautogui.typewrite(command, interval=0.05)
                pyautogui.press('enter')
            return {
                'success': True,
                'response': f"Run dialog opened{f' with {command}' if command else ''}.",
                'response_hi': f"Run डायलॉग खोला{f' - {command}' if command else ''}।"
            }
        return {'success': False, 'response': "Not available"}

    # ═══════════════════════════════════════════════════════════════
    # CLIPBOARD
    # ═══════════════════════════════════════════════════════════════

    def copy_selection(self) -> dict:
        """Copy selected text"""
        if PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.2)
            text = ''
            if CLIPBOARD_AVAILABLE:
                text = pyperclip.paste()
            return {
                'success': True,
                'response': f"Copied: \"{text[:80]}\"" if text else "Copied to clipboard.",
                'response_hi': "क्लिपबोर्ड पर कॉपी किया।"
            }
        return {'success': False, 'response': "Not available"}

    def paste_clipboard(self) -> dict:
        """Paste clipboard content"""
        if PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey('ctrl', 'v')
            return {'success': True, 'response': "Pasted from clipboard.",
                    'response_hi': "क्लिपबोर्ड से पेस्ट किया।"}
        return {'success': False, 'response': "Not available"}

    def set_clipboard(self, text: str) -> dict:
        """Set clipboard content"""
        if CLIPBOARD_AVAILABLE:
            pyperclip.copy(text)
            return {
                'success': True,
                'response': f"Copied to clipboard: \"{text[:60]}\"",
                'response_hi': f"क्लिपबोर्ड में सेट: \"{text[:40]}\""
            }
        return {'success': False, 'response': "Clipboard not available"}

    def get_clipboard(self) -> dict:
        """Read clipboard content"""
        if CLIPBOARD_AVAILABLE:
            text = pyperclip.paste()
            return {
                'success': True,
                'response': f"Clipboard contains: \"{text[:200]}\"",
                'response_hi': f"क्लिपबोर्ड में है: \"{text[:100]}\""
            }
        return {'success': False, 'response': "Clipboard not available"}

    # ═══════════════════════════════════════════════════════════════
    # KEYBOARD SHORTCUTS
    # ═══════════════════════════════════════════════════════════════

    def save_file(self) -> dict:
        """Ctrl+S"""
        if PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey('ctrl', 's')
            return {'success': True, 'response': "File saved.",
                    'response_hi': "फ़ाइल सेव की।"}
        return {'success': False, 'response': "Not available"}

    def save_file_as(self) -> dict:
        """Ctrl+Shift+S"""
        if PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey('ctrl', 'shift', 's')
            return {'success': True, 'response': "Save As dialog opened.",
                    'response_hi': "Save As डायलॉग खोला।"}
        return {'success': False, 'response': "Not available"}

    def select_all(self) -> dict:
        """Ctrl+A"""
        if PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey('ctrl', 'a')
            return {'success': True, 'response': "All selected.",
                    'response_hi': "सब चुन लिया।"}
        return {'success': False, 'response': "Not available"}

    def undo(self) -> dict:
        """Ctrl+Z"""
        if PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey('ctrl', 'z')
            return {'success': True, 'response': "Undone.",
                    'response_hi': "पूर्ववत किया।"}
        return {'success': False, 'response': "Not available"}

    def redo(self) -> dict:
        """Ctrl+Y"""
        if PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey('ctrl', 'y')
            return {'success': True, 'response': "Redone.",
                    'response_hi': "दोबारा किया।"}
        return {'success': False, 'response': "Not available"}

    def new_file(self) -> dict:
        """Ctrl+N"""
        if PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey('ctrl', 'n')
            return {'success': True, 'response': "New file/window opened.",
                    'response_hi': "नई फ़ाइल/विंडो खोली।"}
        return {'success': False, 'response': "Not available"}

    def open_file_dialog(self) -> dict:
        """Ctrl+O"""
        if PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey('ctrl', 'o')
            return {'success': True, 'response': "Open file dialog launched.",
                    'response_hi': "फ़ाइल खोलने का डायलॉग आया।"}
        return {'success': False, 'response': "Not available"}

    def print_document(self) -> dict:
        """Ctrl+P"""
        if PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey('ctrl', 'p')
            return {'success': True, 'response': "Print dialog opened.",
                    'response_hi': "प्रिंट डायलॉग खोला।"}
        return {'success': False, 'response': "Not available"}

    def find_in_page(self, query: str = '') -> dict:
        """Ctrl+F to open find dialog"""
        if PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey('ctrl', 'f')
            if query:
                time.sleep(0.4)
                pyautogui.typewrite(query, interval=0.05)
            return {'success': True, 'response': f"Find dialog opened{f' for {query}' if query else ''}.",
                    'response_hi': f"खोज डायलॉग खोला।"}
        return {'success': False, 'response': "Not available"}

    def press_enter(self) -> dict:
        """Press Enter key"""
        if PYAUTOGUI_AVAILABLE:
            pyautogui.press('enter')
            return {'success': True, 'response': "Enter pressed.",
                    'response_hi': "Enter दबाया।"}
        return {'success': False, 'response': "Not available"}

    def press_escape(self) -> dict:
        """Press Escape key"""
        if PYAUTOGUI_AVAILABLE:
            pyautogui.press('escape')
            return {'success': True, 'response': "Escape pressed.",
                    'response_hi': "Escape दबाया।"}
        return {'success': False, 'response': "Not available"}

    def press_tab(self) -> dict:
        """Press Tab key"""
        if PYAUTOGUI_AVAILABLE:
            pyautogui.press('tab')
            return {'success': True, 'response': "Tab pressed.",
                    'response_hi': "Tab दबाया।"}
        return {'success': False, 'response': "Not available"}

    def press_delete(self) -> dict:
        """Press Delete key"""
        if PYAUTOGUI_AVAILABLE:
            pyautogui.press('delete')
            return {'success': True, 'response': "Delete pressed.",
                    'response_hi': "Delete दबाया।"}
        return {'success': False, 'response': "Not available"}

    def press_backspace(self) -> dict:
        """Press Backspace key"""
        if PYAUTOGUI_AVAILABLE:
            pyautogui.press('backspace')
            return {'success': True, 'response': "Backspace pressed.",
                    'response_hi': "Backspace दबाया।"}
        return {'success': False, 'response': "Not available"}

    # ═══════════════════════════════════════════════════════════════
    # RUN COMMAND / SHELL
    # ═══════════════════════════════════════════════════════════════

    def run_command(self, command: str, visible: bool = True) -> dict:
        """Run a shell command"""
        try:
            if visible:
                # Open CMD with command
                subprocess.Popen(
                    f'start cmd /k "{command}"', shell=True
                )
                return {
                    'success': True,
                    'response': f"Running command: {command}",
                    'response_hi': f"कमांड चला रहा हूँ: {command}"
                }
            else:
                result = subprocess.run(
                    command, shell=True, capture_output=True,
                    text=True, timeout=30,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                output = (result.stdout or result.stderr or 'Done').strip()[:200]
                return {
                    'success': result.returncode == 0,
                    'response': f"Output: {output}",
                    'response_hi': f"परिणाम: {output}"
                }
        except Exception as e:
            return {'success': False, 'response': f"Command failed: {e}"}

    def open_cmd(self) -> dict:
        """Open Command Prompt"""
        subprocess.Popen('cmd.exe', creationflags=subprocess.CREATE_NO_WINDOW)
        return {'success': True, 'response': "Command Prompt opened.",
                'response_hi': "Command Prompt खोला।"}

    def open_powershell(self) -> dict:
        """Open PowerShell"""
        subprocess.Popen('powershell.exe', creationflags=subprocess.CREATE_NO_WINDOW)
        return {'success': True, 'response': "PowerShell opened.",
                'response_hi': "PowerShell खोला।"}

    # ═══════════════════════════════════════════════════════════════
    # CLOSE / KILL APP
    # ═══════════════════════════════════════════════════════════════

    def close_application(self, app_name: str) -> dict:
        """Close/kill an application"""
        name_lower = app_name.lower()
        exe = APP_MAP.get(name_lower, app_name)
        exe_base = os.path.basename(exe)
        if not exe_base.endswith('.exe'):
            exe_base += '.exe'
        try:
            result = subprocess.run(
                ['taskkill', '/f', '/im', exe_base],
                capture_output=True, text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                return {
                    'success': True,
                    'response': f"{app_name} closed.",
                    'response_hi': f"{app_name} बंद किया।"
                }
            # Try by window title via PowerShell
            ps = f'Stop-Process -Name "{name_lower}" -Force -ErrorAction SilentlyContinue'
            subprocess.run(['powershell', '-c', ps],
                           creationflags=subprocess.CREATE_NO_WINDOW,
                           capture_output=True)
            return {
                'success': True,
                'response': f"Attempted to close {app_name}.",
                'response_hi': f"{app_name} बंद करने की कोशिश की।"
            }
        except Exception as e:
            return {'success': False, 'response': f"Could not close {app_name}: {e}"}

    # ═══════════════════════════════════════════════════════════════
    # GET RUNNING APPS
    # ═══════════════════════════════════════════════════════════════

    def list_running_apps(self) -> dict:
        """List currently running applications"""
        if not PSUTIL_AVAILABLE:
            return {'success': False, 'response': "psutil not available"}
        try:
            apps = set()
            for proc in psutil.process_iter(['name', 'status']):
                try:
                    if proc.info['status'] == 'running':
                        name = proc.info['name'].replace('.exe', '')
                        if len(name) > 2 and name.lower() not in (
                            'svchost', 'system', 'idle', 'registry', 'smss',
                            'csrss', 'wininit', 'winlogon', 'services',
                        ):
                            apps.add(name)
                except Exception:
                    pass
            app_list = sorted(apps)[:20]
            return {
                'success': True,
                'response': f"Running apps: {', '.join(app_list[:12])}.",
                'response_hi': f"चल रहे ऐप्स: {', '.join(app_list[:8])}।"
            }
        except Exception as e:
            return {'success': False, 'response': f"Error: {e}"}
