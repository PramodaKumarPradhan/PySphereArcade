"""
ARIA — Office Tasks Skill
MS Office, reminders, timers, notes, calendar
"""

import os
import subprocess
import logging
import datetime
import threading
import json

logger = logging.getLogger(__name__)

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False


class OfficeTasks:
    """Office productivity commands"""

    OFFICE_PATHS = [
        r"C:\Program Files\Microsoft Office\root\Office16",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16",
        r"C:\Program Files\Microsoft Office\Office16",
        r"C:\Program Files (x86)\Microsoft Office\Office16",
        r"C:\Program Files\Microsoft Office\Office15",
    ]

    OFFICE_APPS = {
        'word': 'WINWORD.EXE',
        'excel': 'EXCEL.EXE',
        'powerpoint': 'POWERPNT.EXE',
        'outlook': 'OUTLOOK.EXE',
        'onenote': 'ONENOTE.EXE',
        'access': 'MSACCESS.EXE',
        'publisher': 'MSPUB.EXE',
        'visio': 'VISIO.EXE',
    }

    def __init__(self, config: dict):
        self.config = config
        self._reminders = {}
        self._timers = {}
        self._notes_dir = os.path.expandvars(
            config.get('features', {}).get('notes_dir', '%USERPROFILE%\\Documents\\ARIA Notes')
        )
        os.makedirs(self._notes_dir, exist_ok=True)
        logger.info("OfficeTasks initialized")

    def _find_office_exe(self, exe_name: str) -> str:
        """Find the path to an Office executable"""
        for office_path in self.OFFICE_PATHS:
            full_path = os.path.join(office_path, exe_name)
            if os.path.exists(full_path):
                return full_path
        return exe_name  # Fallback to PATH

    def open_office_app(self, app: str, new_doc: bool = False) -> dict:
        """Open a Microsoft Office application"""
        app_lower = app.lower()
        exe = self.OFFICE_APPS.get(app_lower, f'{app}.exe')
        full_path = self._find_office_exe(exe)

        try:
            subprocess.Popen([full_path], shell=True,
                             creationflags=subprocess.CREATE_NO_WINDOW)
            app_title = app.capitalize()
            return {
                'success': True,
                'response': f"Opening Microsoft {app_title}",
                'response_hi': f"Microsoft {app_title} खोल रहा हूँ"
            }
        except Exception as e:
            # Try via shell
            try:
                os.startfile(exe)
                return {'success': True,
                        'response': f"Opening {app.capitalize()}",
                        'response_hi': f"{app.capitalize()} खोल रहा हूँ"}
            except Exception:
                return {
                    'success': False,
                    'response': f"Could not open {app}. Is Microsoft Office installed?",
                    'response_hi': f"{app} नहीं खुल सका। क्या Microsoft Office इंस्टॉल है?"
                }

    def create_word_document(self, title: str = None) -> dict:
        """Create a new Word document"""
        return self.open_office_app('word', new_doc=True)

    def create_excel_spreadsheet(self, title: str = None) -> dict:
        """Create a new Excel spreadsheet"""
        return self.open_office_app('excel', new_doc=True)

    def create_powerpoint(self, title: str = None) -> dict:
        """Create a new PowerPoint presentation"""
        return self.open_office_app('powerpoint', new_doc=True)

    # ── Notes ────────────────────────────────────────────────────────────────

    def create_note(self, content: str, title: str = None) -> dict:
        """Save a quick note to a text file"""
        try:
            timestamp = datetime.datetime.now()
            title = title or timestamp.strftime('Note_%Y%m%d_%H%M%S')
            filename = f"{title}.txt"
            filepath = os.path.join(self._notes_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Created: {timestamp.strftime('%d %B %Y, %I:%M %p')}\n")
                f.write("=" * 50 + "\n")
                f.write(content + "\n")

            return {
                'success': True,
                'response': f"Note saved as '{filename}'",
                'response_hi': f"नोट '{filename}' सेव किया गया",
                'file': filepath
            }
        except Exception as e:
            return {'success': False, 'response': f"Could not save note: {e}"}

    def open_notes_folder(self) -> dict:
        """Open the ARIA notes folder"""
        try:
            os.startfile(self._notes_dir)
            return {'success': True, 'response': "Opened notes folder",
                    'response_hi': "नोट्स फोल्डर खोला"}
        except Exception as e:
            return {'success': False, 'response': f"Could not open notes: {e}"}

    # ── Timer ────────────────────────────────────────────────────────────────

    def set_timer(self, duration_seconds: int, label: str = 'Timer',
                  callback=None) -> dict:
        """Set a countdown timer"""
        timer_id = f"timer_{len(self._timers)}"
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=duration_seconds)

        def _timer_done():
            msg = f"⏰ {label} is done!"
            msg_hi = f"⏰ {label} समाप्त हो गया!"
            logger.info(f"Timer done: {label}")
            if callback:
                callback({'message': msg, 'message_hi': msg_hi, 'timer_id': timer_id})

        timer = threading.Timer(duration_seconds, _timer_done)
        timer.daemon = True
        timer.start()
        self._timers[timer_id] = {'timer': timer, 'label': label, 'end': end_time}

        mins = duration_seconds // 60
        secs = duration_seconds % 60
        duration_str = f"{mins} minute{'s' if mins != 1 else ''}" if mins else f"{secs} seconds"
        duration_str_hi = f"{mins} मिनट" if mins else f"{secs} सेकंड"

        return {
            'success': True,
            'response': f"Timer set for {duration_str}. I'll let you know when it's done!",
            'response_hi': f"{duration_str_hi} का टाइमर सेट किया। समाप्त होने पर बताऊँगा!",
            'timer_id': timer_id,
            'end_time': end_time.isoformat()
        }

    def cancel_timer(self, timer_id: str = None) -> dict:
        """Cancel a running timer"""
        if timer_id and timer_id in self._timers:
            self._timers[timer_id]['timer'].cancel()
            del self._timers[timer_id]
            return {'success': True, 'response': "Timer cancelled",
                    'response_hi': "टाइमर रद्द किया गया"}
        # Cancel latest timer
        if self._timers:
            latest = list(self._timers.keys())[-1]
            self._timers[latest]['timer'].cancel()
            del self._timers[latest]
            return {'success': True, 'response': "Latest timer cancelled",
                    'response_hi': "अंतिम टाइमर रद्द किया गया"}
        return {'success': False, 'response': "No active timers",
                'response_hi': "कोई सक्रिय टाइमर नहीं"}

    # ── Reminder ─────────────────────────────────────────────────────────────

    def set_reminder(self, message: str, delay_seconds: int,
                     callback=None) -> dict:
        """Set a reminder"""
        reminder_id = f"rem_{len(self._reminders)}"
        remind_time = datetime.datetime.now() + datetime.timedelta(seconds=delay_seconds)

        def _remind():
            logger.info(f"Reminder: {message}")
            if callback:
                callback({
                    'message': f"🔔 Reminder: {message}",
                    'message_hi': f"🔔 याद दिलाना: {message}",
                    'reminder_id': reminder_id
                })

        timer = threading.Timer(delay_seconds, _remind)
        timer.daemon = True
        timer.start()
        self._reminders[reminder_id] = {'timer': timer, 'message': message}

        mins = delay_seconds // 60
        return {
            'success': True,
            'response': f"Reminder set: '{message}' in {mins} minutes",
            'response_hi': f"रिमाइंडर सेट: '{message}' {mins} मिनट में",
            'reminder_id': reminder_id,
            'remind_at': remind_time.strftime('%I:%M %p')
        }

    def get_active_reminders(self) -> dict:
        """List all active reminders and timers"""
        items = []
        for rid, data in self._reminders.items():
            items.append(f"📌 {data['message']}")
        for tid, data in self._timers.items():
            end = data['end'].strftime('%I:%M %p')
            items.append(f"⏱️ {data['label']} — ends at {end}")

        if items:
            return {
                'success': True,
                'response': "Active reminders & timers:\n" + "\n".join(items),
                'response_hi': "सक्रिय रिमाइंडर और टाइमर:\n" + "\n".join(items)
            }
        return {
            'success': True,
            'response': "No active reminders or timers.",
            'response_hi': "कोई सक्रिय रिमाइंडर या टाइमर नहीं।"
        }

    # ── Calendar ─────────────────────────────────────────────────────────────

    def open_calendar(self) -> dict:
        """Open Windows Calendar app"""
        try:
            os.startfile('outlookcal:')
        except Exception:
            try:
                subprocess.Popen('explorer.exe shell:AppsFolder\\microsoft.windowscommunicationsapps_8wekyb3d8bbwe!microsoft.windowslive.calendar', shell=True)
            except Exception:
                import webbrowser
                webbrowser.open('https://calendar.google.com')
        return {'success': True, 'response': "Opening Calendar",
                'response_hi': "कैलेंडर खोल रहा हूँ"}

    def tell_schedule(self) -> dict:
        """Tell today's date and day"""
        now = datetime.datetime.now()
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_names_hi = ['सोमवार', 'मंगलवार', 'बुधवार', 'गुरुवार', 'शुक्रवार', 'शनिवार', 'रविवार']
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        month_names_hi = ['जनवरी', 'फरवरी', 'मार्च', 'अप्रैल', 'मई', 'जून',
                          'जुलाई', 'अगस्त', 'सितंबर', 'अक्टूबर', 'नवंबर', 'दिसंबर']

        day_en = day_names[now.weekday()]
        day_hi = day_names_hi[now.weekday()]
        month_en = month_names[now.month - 1]
        month_hi = month_names_hi[now.month - 1]

        response = f"Today is {day_en}, {now.day} {month_en} {now.year}."
        response_hi = f"आज {day_hi}, {now.day} {month_hi} {now.year} है।"

        return {'success': True, 'response': response, 'response_hi': response_hi}
