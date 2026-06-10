"""
ARIA — Home Control Skill
Night mode, schedules, battery alerts, environment management
"""

import os
import subprocess
import logging
import datetime
import threading

logger = logging.getLogger(__name__)

try:
    import screen_brightness_control as sbc
    SBC_AVAILABLE = True
except Exception:
    SBC_AVAILABLE = False

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False


class HomeControl:
    """Home and environment management commands"""

    def __init__(self, config: dict):
        self.config = config
        self._night_mode = False
        self._water_reminder_timer = None
        self._scheduled_tasks = {}
        logger.info("HomeControl initialized")

    # ── Night / Dark Mode ────────────────────────────────────────────────────

    def night_mode_on(self) -> dict:
        """Activate night mode — lower brightness + warm tone"""
        results = []
        if SBC_AVAILABLE:
            try:
                sbc.set_brightness(30)
                results.append("brightness set to 30%")
            except Exception:
                pass

        # Enable Windows Night Light via registry (requires restart to take effect)
        # We use a simpler approach: just lower brightness and show warm colors suggestion
        self._night_mode = True

        # Also reduce brightness via registry shortcut
        try:
            subprocess.Popen(
                'powershell -Command "& {Add-Type -AssemblyName System.Windows.Forms; '
                '[System.Windows.Forms.SendKeys]::SendWait(\'%{F8}\')}"',
                shell=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
        except Exception:
            pass

        return {
            'success': True,
            'response': "Night mode activated. Brightness reduced for comfortable night use. 🌙",
            'response_hi': "नाइट मोड चालू। रात के लिए चमक कम कर दी गई। 🌙"
        }

    def night_mode_off(self) -> dict:
        """Deactivate night mode — restore brightness"""
        if SBC_AVAILABLE:
            try:
                sbc.set_brightness(80)
            except Exception:
                pass
        self._night_mode = False
        return {
            'success': True,
            'response': "Night mode off. Brightness restored. ☀️",
            'response_hi': "नाइट मोड बंद। चमक वापस की गई। ☀️"
        }

    # ── Scheduled Shutdown ───────────────────────────────────────────────────

    def schedule_shutdown(self, minutes: int) -> dict:
        """Schedule shutdown after N minutes"""
        seconds = minutes * 60
        subprocess.Popen(f'shutdown /s /t {seconds}', shell=True)
        task_id = f'shutdown_{datetime.datetime.now().strftime("%H%M%S")}'
        self._scheduled_tasks[task_id] = {'type': 'shutdown', 'at': minutes}

        return {
            'success': True,
            'response': f"Shutdown scheduled in {minutes} minutes. Say 'cancel shutdown' to abort.",
            'response_hi': f"{minutes} मिनट में शटडाउन शेड्यूल किया। रद्द करने के लिए कहें 'शटडाउन रद्द करो'।"
        }

    def cancel_shutdown(self) -> dict:
        """Cancel any scheduled shutdown"""
        subprocess.Popen('shutdown /a', shell=True)
        return {
            'success': True,
            'response': "Shutdown cancelled. Your PC will continue running. ✅",
            'response_hi': "शटडाउन रद्द किया। आपका PC चलता रहेगा। ✅"
        }

    # ── Water Reminder ────────────────────────────────────────────────────────

    def start_water_reminders(self, interval_minutes: int = 60,
                               callback=None) -> dict:
        """Start periodic water drinking reminders"""
        if self._water_reminder_timer:
            self._water_reminder_timer.cancel()

        def _remind():
            if callback:
                callback({
                    'message': "💧 Reminder: Time to drink some water! Stay hydrated.",
                    'message_hi': "💧 याद दिलाना: पानी पीने का समय! हाइड्रेटेड रहें।"
                })
            # Schedule next reminder
            self._water_reminder_timer = threading.Timer(
                interval_minutes * 60, _remind)
            self._water_reminder_timer.daemon = True
            self._water_reminder_timer.start()

        self._water_reminder_timer = threading.Timer(interval_minutes * 60, _remind)
        self._water_reminder_timer.daemon = True
        self._water_reminder_timer.start()

        return {
            'success': True,
            'response': f"Water reminders started! I'll remind you every {interval_minutes} minutes. 💧",
            'response_hi': f"पानी के रिमाइंडर शुरू! हर {interval_minutes} मिनट में याद दिलाऊँगा। 💧"
        }

    def stop_water_reminders(self) -> dict:
        """Stop water reminders"""
        if self._water_reminder_timer:
            self._water_reminder_timer.cancel()
            self._water_reminder_timer = None
        return {
            'success': True,
            'response': "Water reminders stopped.",
            'response_hi': "पानी के रिमाइंडर बंद किए।"
        }

    # ── Do Not Disturb ───────────────────────────────────────────────────────

    def focus_mode(self) -> dict:
        """Enable Windows Focus Assist (Do Not Disturb)"""
        try:
            # Open Focus Assist settings
            subprocess.Popen('ms-settings:quiethours', shell=True)
            return {
                'success': True,
                'response': "Opened Focus Assist settings. Enable it to silence notifications. 🎯",
                'response_hi': "फोकस असिस्ट सेटिंग खोली। नोटिफिकेशन बंद करें। 🎯"
            }
        except Exception:
            return {'success': False, 'response': "Could not open Focus Assist"}

    # ── Environment Commands ─────────────────────────────────────────────────

    def check_environment(self) -> dict:
        """General environment status"""
        import psutil
        battery = psutil.sensors_battery()
        hour = datetime.datetime.now().hour

        tips = []
        tips_hi = []

        if battery and not battery.power_plugged and battery.percent < 30:
            tips.append("⚠️ Low battery — please plug in charger")
            tips_hi.append("⚠️ बैटरी कम — चार्जर लगाएं")

        if hour >= 22 or hour < 6:
            tips.append("🌙 It's late night — consider night mode")
            tips_hi.append("🌙 देर रात है — नाइट मोड चालू करें")
        elif hour >= 18:
            tips.append("🌆 Evening — good time to wrap up work")
            tips_hi.append("🌆 शाम है — काम समेटने का समय")

        if not tips:
            tips = ["✅ Environment looks good! Keep working!"]
            tips_hi = ["✅ सब ठीक है! काम जारी रखें!"]

        return {
            'success': True,
            'response': "\n".join(tips),
            'response_hi': "\n".join(tips_hi)
        }

    def open_task_scheduler(self) -> dict:
        """Open Windows Task Scheduler"""
        subprocess.Popen('taskschd.msc', shell=True)
        return {
            'success': True,
            'response': "Opening Windows Task Scheduler",
            'response_hi': "Windows Task Scheduler खोल रहा हूँ"
        }

    def open_control_panel(self) -> dict:
        """Open Control Panel"""
        subprocess.Popen('control.exe', shell=True)
        return {
            'success': True,
            'response': "Opening Control Panel",
            'response_hi': "Control Panel खोल रहा हूँ"
        }

    def empty_recycle_bin(self) -> dict:
        """Empty the Recycle Bin"""
        try:
            import winshell
            winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
            return {'success': True, 'response': "Recycle Bin emptied! 🗑️",
                    'response_hi': "रीसायकल बिन खाली किया! 🗑️"}
        except ImportError:
            subprocess.Popen(
                'PowerShell.exe -Command "Clear-RecycleBin -Force"',
                shell=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            return {'success': True, 'response': "Recycle Bin emptied! 🗑️",
                    'response_hi': "रीसायकल बिन खाली किया! 🗑️"}
        except Exception as e:
            return {'success': False, 'response': f"Could not empty bin: {e}"}

    def control_smart_home(self, device: str, state: str, value: str = None) -> dict:
        """Simulate smart home device control"""
        device_clean = device.strip().lower()
        state_clean = state.strip().lower()
        state_en = "on" if state_clean in ['on', 'turn on', 'enable', 'start', 'chalu', 'one'] else "off"
        state_hi = "चालू" if state_en == "on" else "बंद"

        if any(w in device_clean for w in ['temp', 'thermostat', 'temperature', 'ac temperature']):
            val_str = value or "22"
            return {
                'success': True,
                'response': f"🌡️ Setting the thermostat to {val_str} degrees.",
                'response_hi': f"🌡️ थर्मोस्टेट का तापमान {val_str} डिग्री पर सेट कर रहा हूँ।"
            }

        icon = "💡" if any(w in device_clean for w in ['light', 'lamp', 'bulb', 'led']) else (
            "🌀" if any(w in device_clean for w in ['fan', 'ac', 'cooler', 'blow']) else "🔌"
        )

        return {
            'success': True,
            'response': f"{icon} Turning {state_en} the {device_clean}.",
            'response_hi': f"{icon} {device_clean} {state_hi} कर रहा हूँ।"
        }

