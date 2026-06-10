"""
ARIA — System Control Skill
Handles OS-level commands: apps, volume, brightness, power, screenshots
"""

import os
import sys
import subprocess
import logging
import time
import datetime

logger = logging.getLogger(__name__)

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    PYCAW_AVAILABLE = True
except Exception:
    PYCAW_AVAILABLE = False

try:
    import screen_brightness_control as sbc
    SBC_AVAILABLE = True
except Exception:
    SBC_AVAILABLE = False


class SystemControl:
    """Laptop / Windows OS control commands"""

    # Common Windows application paths/names
    APP_MAP = {
        # Productivity
        'notepad': 'notepad.exe',
        'calculator': 'calc.exe',
        'paint': 'mspaint.exe',
        'wordpad': 'wordpad.exe',
        'calendar': 'explorer.exe shell:AppsFolder\\microsoft.windowscommunicationsapps_8wekyb3d8bbwe!microsoft.windowslive.calendar',
        'clock': 'explorer.exe shell:AppsFolder\\Microsoft.WindowsAlarms_8wekyb3d8bbwe!App',
        'snipping tool': 'SnippingTool.exe',
        'snip': 'SnippingTool.exe',
        'sticky notes': 'stikynot.exe',
        'task manager': 'taskmgr.exe',
        'device manager': 'devmgmt.msc',
        'control panel': 'control.exe',
        'settings': 'ms-settings:',
        'registry': 'regedit.exe',
        'cmd': 'cmd.exe',
        'command prompt': 'cmd.exe',
        'powershell': 'powershell.exe',
        'file explorer': 'explorer.exe',
        'explorer': 'explorer.exe',

        # Microsoft Office
        'word': 'WINWORD.EXE',
        'excel': 'EXCEL.EXE',
        'powerpoint': 'POWERPNT.EXE',
        'outlook': 'OUTLOOK.EXE',
        'teams': 'teams.exe',
        'onenote': 'ONENOTE.EXE',
        'access': 'MSACCESS.EXE',

        # Browsers
        'chrome': 'chrome.exe',
        'firefox': 'firefox.exe',
        'edge': 'msedge.exe',
        'browser': 'msedge.exe',
        'internet': 'msedge.exe',

        # Media
        'vlc': 'vlc.exe',
        'media player': 'wmplayer.exe',
        'windows media player': 'wmplayer.exe',
        'spotify': 'spotify.exe',
        'groove': 'mswindowsmusic:',

        # Communication
        'whatsapp': 'whatsapp.exe',
        'telegram': 'telegram.exe',
        'zoom': 'zoom.exe',
        'skype': 'skype.exe',

        # System Tools
        'camera': 'microsoft.windows.camera:',
        'photos': 'ms-photos:',
        'store': 'ms-windows-store:',
        'cortana': 'ms-cortana:',
    }

    def __init__(self, config: dict):
        self.config = config
        self._volume_interface = None
        if PYCAW_AVAILABLE:
            self._init_volume()
        logger.info("SystemControl initialized")

    def _init_volume(self):
        """Initialize Windows audio volume interface"""
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self._volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
        except Exception as e:
            # Try alternative pycaw API (newer versions)
            try:
                from pycaw.pycaw import AudioDevice
                sessions = AudioUtilities.GetAllSessions()
                self._volume_interface = None
                logger.warning(f"Volume via pycaw not available, using pyautogui fallback: {e}")
            except Exception:
                logger.warning(f"Volume interface init failed: {e}")

    # ── Application Control ──────────────────────────────────────────────────

    def open_application(self, app_name: str) -> dict:
        """Open an application by name"""
        app_lower = app_name.strip().lower()
        exe = self.APP_MAP.get(app_lower)

        if exe:
            try:
                if exe.startswith('ms-') or exe.startswith('microsoft.') or 'shell:' in exe:
                    os.startfile(exe)
                else:
                    subprocess.Popen(exe, shell=True,
                                     creationflags=subprocess.CREATE_NO_WINDOW)
                return {'success': True, 'response': f"Opening {app_name}",
                        'response_hi': f"{app_name} खोल रहा हूँ"}
            except Exception as e:
                logger.error(f"Failed to open {app_name}: {e}")
                return {'success': False, 'response': f"Could not open {app_name}: {e}"}
        else:
            # Try running directly
            try:
                subprocess.Popen(app_name, shell=True,
                                 creationflags=subprocess.CREATE_NO_WINDOW)
                return {'success': True, 'response': f"Opening {app_name}",
                        'response_hi': f"{app_name} खोल रहा हूँ"}
            except Exception:
                return {'success': False,
                        'response': f"I couldn't find '{app_name}'. Try the exact app name.",
                        'response_hi': f"'{app_name}' नहीं मिला। सटीक नाम बताएं।"}

    def close_application(self, app_name: str) -> dict:
        """Close/kill an application by name"""
        exe = self.APP_MAP.get(app_name.lower(), app_name)
        exe_name = os.path.basename(exe).replace('.exe', '')
        try:
            result = subprocess.run(['taskkill', '/f', '/im', f'{exe_name}.exe'],
                                    capture_output=True, text=True)
            if result.returncode == 0:
                return {'success': True, 'response': f"{app_name} has been closed.",
                        'response_hi': f"{app_name} बंद कर दिया गया।"}
            else:
                return {'success': False, 'response': f"Could not close {app_name}. Is it running?",
                        'response_hi': f"{app_name} बंद नहीं हो सका। क्या यह चल रहा है?"}
        except Exception as e:
            return {'success': False, 'response': f"Error closing {app_name}: {e}"}

    # ── Volume Control ───────────────────────────────────────────────────────

    def volume_up(self, step: int = 10) -> dict:
        """Increase system volume by step%"""
        if PYCAW_AVAILABLE and self._volume_interface:
            try:
                current = self._volume_interface.GetMasterVolumeLevelScalar()
                new_vol = min(1.0, current + step / 100.0)
                self._volume_interface.SetMasterVolumeLevelScalar(new_vol, None)
                pct = int(new_vol * 100)
                return {'success': True, 'response': f"Volume set to {pct}%",
                        'response_hi': f"आवाज़ {pct}% कर दी गई"}
            except Exception as e:
                logger.error(f"Volume up error: {e}")

        if PYAUTOGUI_AVAILABLE:
            for _ in range(step // 2):
                pyautogui.press('volumeup')
            return {'success': True, 'response': "Volume increased",
                    'response_hi': "आवाज़ बढ़ा दी"}
        return {'success': False, 'response': "Volume control not available"}

    def volume_down(self, step: int = 10) -> dict:
        """Decrease system volume by step%"""
        if PYCAW_AVAILABLE and self._volume_interface:
            try:
                current = self._volume_interface.GetMasterVolumeLevelScalar()
                new_vol = max(0.0, current - step / 100.0)
                self._volume_interface.SetMasterVolumeLevelScalar(new_vol, None)
                pct = int(new_vol * 100)
                return {'success': True, 'response': f"Volume set to {pct}%",
                        'response_hi': f"आवाज़ {pct}% कर दी गई"}
            except Exception:
                pass

        if PYAUTOGUI_AVAILABLE:
            for _ in range(step // 2):
                pyautogui.press('volumedown')
            return {'success': True, 'response': "Volume decreased",
                    'response_hi': "आवाज़ कम कर दी"}
        return {'success': False, 'response': "Volume control not available"}

    def mute_volume(self) -> dict:
        """Toggle mute"""
        if PYCAW_AVAILABLE and self._volume_interface:
            try:
                muted = self._volume_interface.GetMute()
                self._volume_interface.SetMute(not muted, None)
                state = "muted" if not muted else "unmuted"
                state_hi = "म्यूट" if not muted else "अनम्यूट"
                return {'success': True, 'response': f"Volume {state}",
                        'response_hi': f"आवाज़ {state_hi} की गई"}
            except Exception:
                pass

        if PYAUTOGUI_AVAILABLE:
            pyautogui.press('volumemute')
            return {'success': True, 'response': "Volume toggled",
                    'response_hi': "आवाज़ टॉगल की गई"}
        return {'success': False, 'response': "Mute not available"}

    def set_volume(self, level: int) -> dict:
        """Set volume to specific level (0-100)"""
        level = max(0, min(100, level))
        if PYCAW_AVAILABLE and self._volume_interface:
            try:
                self._volume_interface.SetMasterVolumeLevelScalar(level / 100.0, None)
                return {'success': True, 'response': f"Volume set to {level}%",
                        'response_hi': f"आवाज़ {level}% पर सेट की"}
            except Exception:
                pass
        return {'success': False, 'response': "Could not set volume"}

    def get_volume(self) -> int:
        """Get current volume level (0-100)"""
        if PYCAW_AVAILABLE and self._volume_interface:
            try:
                vol = self._volume_interface.GetMasterVolumeLevelScalar()
                return int(vol * 100)
            except Exception:
                pass
        return -1

    # ── Brightness Control ───────────────────────────────────────────────────

    def brightness_up(self, step: int = 10) -> dict:
        if SBC_AVAILABLE:
            try:
                current = sbc.get_brightness()[0]
                new_b = min(100, current + step)
                sbc.set_brightness(new_b)
                return {'success': True, 'response': f"Brightness set to {new_b}%",
                        'response_hi': f"चमक {new_b}% कर दी"}
            except Exception as e:
                return {'success': False, 'response': f"Brightness error: {e}"}
        return {'success': False, 'response': "Brightness control not available on this device"}

    def brightness_down(self, step: int = 10) -> dict:
        if SBC_AVAILABLE:
            try:
                current = sbc.get_brightness()[0]
                new_b = max(10, current - step)
                sbc.set_brightness(new_b)
                return {'success': True, 'response': f"Brightness set to {new_b}%",
                        'response_hi': f"चमक {new_b}% कर दी"}
            except Exception as e:
                return {'success': False, 'response': f"Brightness error: {e}"}
        return {'success': False, 'response': "Brightness control not available on this device"}

    def get_brightness(self) -> int:
        if SBC_AVAILABLE:
            try:
                return sbc.get_brightness()[0]
            except Exception:
                pass
        return -1

    # ── Power Management ─────────────────────────────────────────────────────

    def shutdown(self, delay: int = 10) -> dict:
        """Schedule system shutdown"""
        subprocess.Popen(f'shutdown /s /t {delay}', shell=True)
        return {'success': True,
                'response': f"System will shut down in {delay} seconds. Say 'cancel shutdown' to abort.",
                'response_hi': f"सिस्टम {delay} सेकंड में बंद होगा। रद्द करने के लिए कहें 'शटडाउन रद्द करो'"}

    def restart(self, delay: int = 10) -> dict:
        """Schedule system restart"""
        subprocess.Popen(f'shutdown /r /t {delay}', shell=True)
        return {'success': True,
                'response': f"System will restart in {delay} seconds.",
                'response_hi': f"सिस्टम {delay} सेकंड में रीस्टार्ट होगा।"}

    def cancel_shutdown(self) -> dict:
        """Cancel scheduled shutdown"""
        subprocess.Popen('shutdown /a', shell=True)
        return {'success': True, 'response': "Shutdown cancelled",
                'response_hi': "शटडाउन रद्द किया गया"}

    def sleep(self) -> dict:
        """Put system to sleep"""
        subprocess.Popen('rundll32.exe powrprof.dll,SetSuspendState 0,1,0', shell=True)
        return {'success': True, 'response': "Going to sleep. Goodnight!",
                'response_hi': "नींद मोड में जा रहा हूँ। शुभ रात्रि!"}

    def lock_screen(self) -> dict:
        """Lock the screen"""
        import ctypes
        ctypes.windll.user32.LockWorkStation()
        return {'success': True, 'response': "Screen locked",
                'response_hi': "स्क्रीन लॉक कर दी"}

    # ── Screenshot ───────────────────────────────────────────────────────────

    def take_screenshot(self, save_dir: str = None) -> dict:
        """Take a screenshot and save it"""
        if not PYAUTOGUI_AVAILABLE:
            return {'success': False, 'response': "Screenshot not available (pyautogui missing)"}

        try:
            save_dir = save_dir or os.path.expandvars(
                self.config.get('features', {}).get('screenshot_dir', '%USERPROFILE%\\Desktop'))
            os.makedirs(save_dir, exist_ok=True)

            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'ARIA_Screenshot_{timestamp}.png'
            filepath = os.path.join(save_dir, filename)

            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)

            return {'success': True,
                    'response': f"Screenshot saved as {filename} on Desktop",
                    'response_hi': f"स्क्रीनशॉट डेस्कटॉप पर {filename} सेव किया गया",
                    'file': filepath}
        except Exception as e:
            return {'success': False, 'response': f"Screenshot failed: {e}"}

    # ── Keyboard Shortcuts ───────────────────────────────────────────────────

    def minimize_all(self) -> dict:
        """Minimize all windows (Win+D)"""
        if PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey('win', 'd')
            return {'success': True, 'response': "All windows minimized",
                    'response_hi': "सभी विंडो छोटी की गईं"}
        return {'success': False, 'response': "Not available"}

    def show_desktop(self) -> dict:
        return self.minimize_all()

    def copy(self) -> dict:
        if PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey('ctrl', 'c')
            return {'success': True, 'response': "Copied to clipboard",
                    'response_hi': "क्लिपबोर्ड पर कॉपी किया गया"}
        return {'success': False, 'response': "Not available"}

    def paste(self) -> dict:
        if PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey('ctrl', 'v')
            return {'success': True, 'response': "Pasted from clipboard",
                    'response_hi': "क्लिपबोर्ड से पेस्ट किया गया"}
        return {'success': False, 'response': "Not available"}

    def press_key(self, key: str) -> dict:
        if PYAUTOGUI_AVAILABLE:
            pyautogui.press(key)
            return {'success': True, 'response': f"Pressed {key}"}
        return {'success': False, 'response': "Not available"}

    def open_task_manager(self) -> dict:
        return self.open_application('task manager')

    def open_settings(self) -> dict:
        return self.open_application('settings')

    def set_wifi(self, state: bool) -> dict:
        """Enable or disable Wi-Fi network interface"""
        admin_state = "enabled" if state else "disabled"
        state_str = "on" if state else "off"
        state_str_hi = "चालू" if state else "बंद"
        cmd = f'netsh interface set interface "Wi-Fi" admin={admin_state}'
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if "Access is denied" in result.stderr or result.returncode != 0:
                logger.warning(f"Wi-Fi control requires Admin privileges: {result.stderr}")
                return {
                    'success': False,
                    'response': "I couldn't toggle Wi-Fi. This action requires running ARIA as Administrator.",
                    'response_hi': "मैं वाई-फाई को टॉगल नहीं कर सका। इसके लिए ARIA को प्रशासक (Administrator) के रूप में चलाना होगा।"
                }
            return {
                'success': True,
                'response': f"Wi-Fi has been turned {state_str}.",
                'response_hi': f"वाई-फाई {state_str_hi} कर दिया गया है।"
            }
        except Exception as e:
            logger.error(f"Failed to set Wi-Fi state: {e}")
            return {'success': False, 'response': f"Error toggling Wi-Fi: {e}"}

    def set_bluetooth(self, state: bool) -> dict:
        """Enable or disable Bluetooth device using PowerShell"""
        pnp_state = "Enable-PnpDevice" if state else "Disable-PnpDevice"
        state_str = "on" if state else "off"
        state_str_hi = "चालू" if state else "बंद"
        ps_cmd = f"Get-PnpDevice -Class Bluetooth -Status OK,Error,Unknown | Where-Object {{$_.InstanceId -match 'BTHENUM|USB\\\\VID_'}} | {pnp_state} -Confirm:$false"
        full_cmd = ["powershell", "-Command", ps_cmd]
        try:
            result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0 or "PermissionDenied" in result.stderr or "AccessDenied" in result.stderr:
                logger.warning(f"Bluetooth control requires Admin privileges: {result.stderr}")
                return {
                    'success': False,
                    'response': "I couldn't toggle Bluetooth. This action requires running ARIA as Administrator.",
                    'response_hi': "मैं ब्लूटूथ को टॉगल नहीं कर सका। इसके लिए ARIA को प्रशासक (Administrator) के रूप में चलाना होगा।"
                }
            return {
                'success': True,
                'response': f"Bluetooth has been turned {state_str}.",
                'response_hi': f"ब्लूटूथ {state_str_hi} कर दिया गया है।"
            }
        except Exception as e:
            logger.error(f"Failed to set Bluetooth state: {e}")
            return {'success': False, 'response': f"Error toggling Bluetooth: {e}"}

    def set_airplane_mode(self, state: bool) -> dict:
        """Toggle Airplane Mode (opens settings page)"""
        state_str = "on" if state else "off"
        state_str_hi = "चालू" if state else "बंद"
        try:
            os.startfile('ms-settings:network-airplanemode')
            return {
                'success': True,
                'response': f"Opening Airplane Mode settings. Please toggle it {state_str} there.",
                'response_hi': f"हवाई जहाज (Airplane) मोड सेटिंग्स खोल रहा हूँ। कृपया वहाँ इसे {state_str_hi} करें।"
            }
        except Exception as e:
            logger.error(f"Failed to open airplane mode settings: {e}")
            return {'success': False, 'response': f"Could not toggle Airplane Mode: {e}"}

