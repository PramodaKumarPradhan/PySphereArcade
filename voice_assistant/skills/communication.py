"""
ARIA — Communication Skill
Email, WhatsApp Web, communication apps
"""

import webbrowser
import urllib.parse
import logging
import subprocess
import os

logger = logging.getLogger(__name__)


class Communication:
    """Communication-related commands"""

    def __init__(self, config: dict):
        self.config = config
        logger.info("Communication skill initialized")

    def open_gmail(self) -> dict:
        webbrowser.open('https://mail.google.com')
        return {'success': True, 'response': "Opening Gmail 📧",
                'response_hi': "Gmail खोल रहा हूँ 📧"}

    def open_outlook(self) -> dict:
        """Open Outlook desktop app or web"""
        try:
            subprocess.Popen('OUTLOOK.EXE', shell=True,
                             creationflags=subprocess.CREATE_NO_WINDOW)
            return {'success': True, 'response': "Opening Microsoft Outlook 📧",
                    'response_hi': "Microsoft Outlook खोल रहा हूँ 📧"}
        except Exception:
            webbrowser.open('https://outlook.live.com')
            return {'success': True, 'response': "Opening Outlook Web 📧",
                    'response_hi': "Outlook Web खोल रहा हूँ 📧"}

    def compose_email(self, to: str = '', subject: str = '', body: str = '') -> dict:
        """Open Gmail compose or mailto"""
        if to or subject or body:
            params = {}
            if subject:
                params['subject'] = subject
            if body:
                params['body'] = body
            query = urllib.parse.urlencode(params)
            url = f"https://mail.google.com/mail/?view=cm&to={urllib.parse.quote(to)}&{query}"
        else:
            url = "https://mail.google.com/mail/?view=cm"
        webbrowser.open(url)
        return {
            'success': True,
            'response': "Opening Gmail compose window ✉️",
            'response_hi': "Gmail में नया ईमेल लिख रहा हूँ ✉️"
        }

    def open_whatsapp(self) -> dict:
        """Open WhatsApp (desktop or web)"""
        # Try desktop app first
        whatsapp_paths = [
            os.path.expandvars('%LOCALAPPDATA%\\WhatsApp\\WhatsApp.exe'),
            r'C:\Program Files\WindowsApps\WhatsApp',
        ]
        for path in whatsapp_paths:
            if os.path.exists(path):
                try:
                    subprocess.Popen([path])
                    return {'success': True, 'response': "Opening WhatsApp 💬",
                            'response_hi': "WhatsApp खोल रहा हूँ 💬"}
                except Exception:
                    pass

        # Try Windows Store app
        try:
            subprocess.Popen('explorer.exe shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!WhatsApp', shell=True)
            return {'success': True, 'response': "Opening WhatsApp 💬",
                    'response_hi': "WhatsApp खोल रहा हूँ 💬"}
        except Exception:
            pass

        # Fallback: Web
        webbrowser.open('https://web.whatsapp.com')
        return {'success': True, 'response': "Opening WhatsApp Web 💬",
                'response_hi': "WhatsApp Web खोल रहा हूँ 💬"}

    def send_whatsapp_message(self, phone: str, message: str) -> dict:
        """Open WhatsApp web with pre-filled message"""
        encoded_msg = urllib.parse.quote(message)
        phone_clean = phone.replace('+', '').replace('-', '').replace(' ', '')
        url = f"https://web.whatsapp.com/send?phone={phone_clean}&text={encoded_msg}"
        webbrowser.open(url)
        return {
            'success': True,
            'response': f"Opening WhatsApp to send message to {phone}",
            'response_hi': f"{phone} को WhatsApp मैसेज के लिए खोल रहा हूँ"
        }

    def open_teams(self) -> dict:
        """Open Microsoft Teams"""
        try:
            subprocess.Popen('teams.exe', shell=True,
                             creationflags=subprocess.CREATE_NO_WINDOW)
            return {'success': True, 'response': "Opening Microsoft Teams 💼",
                    'response_hi': "Microsoft Teams खोल रहा हूँ 💼"}
        except Exception:
            webbrowser.open('https://teams.microsoft.com')
            return {'success': True, 'response': "Opening Teams in browser 💼",
                    'response_hi': "ब्राउज़र में Teams खोल रहा हूँ 💼"}

    def open_zoom(self) -> dict:
        """Open Zoom"""
        try:
            subprocess.Popen('zoom.exe', shell=True,
                             creationflags=subprocess.CREATE_NO_WINDOW)
            return {'success': True, 'response': "Opening Zoom 📹",
                    'response_hi': "Zoom खोल रहा हूँ 📹"}
        except Exception:
            webbrowser.open('https://zoom.us/join')
            return {'success': True, 'response': "Opening Zoom Web 📹",
                    'response_hi': "Zoom Web खोल रहा हूँ 📹"}

    def open_skype(self) -> dict:
        """Open Skype"""
        try:
            subprocess.Popen('skype.exe', shell=True,
                             creationflags=subprocess.CREATE_NO_WINDOW)
            return {'success': True, 'response': "Opening Skype 📞",
                    'response_hi': "Skype खोल रहा हूँ 📞"}
        except Exception:
            webbrowser.open('https://web.skype.com')
            return {'success': True, 'response': "Opening Skype Web 📞",
                    'response_hi': "Skype Web खोल रहा हूँ 📞"}

    def open_telegram(self) -> dict:
        """Open Telegram"""
        try:
            subprocess.Popen('telegram.exe', shell=True,
                             creationflags=subprocess.CREATE_NO_WINDOW)
            return {'success': True, 'response': "Opening Telegram ✈️",
                    'response_hi': "Telegram खोल रहा हूँ ✈️"}
        except Exception:
            webbrowser.open('https://web.telegram.org')
            return {'success': True, 'response': "Opening Telegram Web ✈️",
                    'response_hi': "Telegram Web खोल रहा हूँ ✈️"}

    def start_google_meet(self) -> dict:
        """Start a new Google Meet"""
        webbrowser.open('https://meet.google.com/new')
        return {'success': True, 'response': "Starting a new Google Meet 📹",
                'response_hi': "नया Google Meet शुरू कर रहा हूँ 📹"}
