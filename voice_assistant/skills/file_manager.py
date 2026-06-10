"""
ARIA — File Manager Skill
Navigate folders, find files, manage common locations
"""

import os
import subprocess
import logging
import glob
import shutil

logger = logging.getLogger(__name__)

COMMON_PATHS = {
    'desktop': os.path.expandvars('%USERPROFILE%\\Desktop'),
    'downloads': os.path.expandvars('%USERPROFILE%\\Downloads'),
    'documents': os.path.expandvars('%USERPROFILE%\\Documents'),
    'pictures': os.path.expandvars('%USERPROFILE%\\Pictures'),
    'music': os.path.expandvars('%USERPROFILE%\\Music'),
    'videos': os.path.expandvars('%USERPROFILE%\\Videos'),
    'onedrive': os.path.expandvars('%USERPROFILE%\\OneDrive'),
    'appdata': os.path.expandvars('%APPDATA%'),
    'temp': os.path.expandvars('%TEMP%'),
    'c drive': 'C:\\',
    'c:': 'C:\\',
    'd drive': 'D:\\',
    'd:': 'D:\\',
    'program files': r'C:\Program Files',
    'startup': os.path.expandvars('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup'),
    'recycle bin': 'shell:RecycleBinFolder',
}


class FileManager:
    """File system navigation and management commands"""

    def __init__(self, config: dict):
        self.config = config
        logger.info("FileManager initialized")

    def open_folder(self, folder_name: str) -> dict:
        """Open a folder in Windows Explorer"""
        folder_lower = folder_name.strip().lower()

        # Check known paths
        if folder_lower in COMMON_PATHS:
            path = COMMON_PATHS[folder_lower]
        elif os.path.exists(folder_name):
            path = folder_name
        else:
            # Try expanding as environment variable
            expanded = os.path.expandvars(folder_name)
            if os.path.exists(expanded):
                path = expanded
            else:
                # Search in common locations
                return self.find_folder(folder_name)

        try:
            if path.startswith('shell:'):
                subprocess.Popen(f'explorer.exe {path}', shell=True)
            else:
                os.startfile(path)
            folder_display = folder_name.title()
            return {
                'success': True,
                'response': f"Opening {folder_display} folder",
                'response_hi': f"{folder_display} फोल्डर खोल रहा हूँ"
            }
        except Exception as e:
            return {'success': False, 'response': f"Could not open folder: {e}"}

    def open_downloads(self) -> dict:
        return self.open_folder('downloads')

    def open_documents(self) -> dict:
        return self.open_folder('documents')

    def open_desktop(self) -> dict:
        return self.open_folder('desktop')

    def open_pictures(self) -> dict:
        return self.open_folder('pictures')

    def open_music(self) -> dict:
        return self.open_folder('music')

    def open_videos(self) -> dict:
        return self.open_folder('videos')

    def open_onedrive(self) -> dict:
        return self.open_folder('onedrive')

    def open_file_explorer(self) -> dict:
        """Open Windows File Explorer at This PC"""
        subprocess.Popen('explorer.exe', shell=True)
        return {
            'success': True,
            'response': "Opening File Explorer",
            'response_hi': "File Explorer खोल रहा हूँ"
        }

    def find_file(self, filename: str, search_path: str = None) -> dict:
        """Search for a file in common locations"""
        search_dirs = [
            COMMON_PATHS['desktop'],
            COMMON_PATHS['downloads'],
            COMMON_PATHS['documents'],
            COMMON_PATHS['pictures'],
        ]
        if search_path:
            search_dirs.insert(0, search_path)

        found = []
        for directory in search_dirs:
            if not os.path.exists(directory):
                continue
            pattern = os.path.join(directory, f'*{filename}*')
            matches = glob.glob(pattern, recursive=False)
            found.extend(matches[:5])  # Limit results per dir

            # Also check subdirectories (shallow)
            try:
                for item in os.listdir(directory):
                    subdir = os.path.join(directory, item)
                    if os.path.isdir(subdir):
                        subpattern = os.path.join(subdir, f'*{filename}*')
                        sub_matches = glob.glob(subpattern)
                        found.extend(sub_matches[:3])
            except PermissionError:
                pass

            if len(found) >= 10:
                break

        if found:
            response = f"Found {len(found)} file(s) matching '{filename}':\n"
            response += "\n".join(f"• {os.path.basename(f)} ({os.path.dirname(f)})" for f in found[:5])
            if len(found) > 5:
                response += f"\n... and {len(found) - 5} more."

            # Open first match
            try:
                os.startfile(os.path.dirname(found[0]))
            except Exception:
                pass

            return {
                'success': True,
                'response': response,
                'response_hi': f"'{filename}' से मेल खाती {len(found)} फ़ाइल(ें) मिलीं",
                'files': found
            }
        else:
            # Open Windows Search
            subprocess.Popen(f'explorer.exe /root,search-ms:query={filename}', shell=True)
            return {
                'success': True,
                'response': f"No quick match found. Opened Windows Search for '{filename}'",
                'response_hi': f"'{filename}' की Windows Search खोली"
            }

    def find_folder(self, folder_name: str) -> dict:
        """Search for a folder"""
        search_dirs = list(COMMON_PATHS.values())
        found = []

        for directory in search_dirs:
            if not os.path.isdir(str(directory)):
                continue
            try:
                for item in os.listdir(directory):
                    if folder_name.lower() in item.lower():
                        full_path = os.path.join(directory, item)
                        if os.path.isdir(full_path):
                            found.append(full_path)
            except (PermissionError, OSError):
                pass

        if found:
            os.startfile(found[0])
            return {
                'success': True,
                'response': f"Found and opened '{os.path.basename(found[0])}'",
                'response_hi': f"'{os.path.basename(found[0])}' मिला और खोला"
            }

        return {
            'success': False,
            'response': f"Folder '{folder_name}' not found",
            'response_hi': f"'{folder_name}' फोल्डर नहीं मिला"
        }

    def create_folder(self, folder_name: str, location: str = 'desktop') -> dict:
        """Create a new folder"""
        base_path = COMMON_PATHS.get(location.lower(), COMMON_PATHS['desktop'])
        folder_path = os.path.join(base_path, folder_name)

        try:
            os.makedirs(folder_path, exist_ok=True)
            os.startfile(folder_path)
            return {
                'success': True,
                'response': f"Created folder '{folder_name}' on {location}",
                'response_hi': f"'{folder_name}' फोल्डर {location} पर बनाया"
            }
        except Exception as e:
            return {'success': False, 'response': f"Could not create folder: {e}"}

    def disk_usage(self) -> dict:
        """Show disk usage for main drives"""
        import psutil
        try:
            drives = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    free_gb = usage.free / (1024**3)
                    total_gb = usage.total / (1024**3)
                    drives.append(
                        f"Drive {partition.mountpoint}: {free_gb:.1f}GB free / {total_gb:.1f}GB total"
                    )
                except PermissionError:
                    pass

            response = "Disk usage:\n" + "\n".join(drives)
            return {'success': True, 'response': response,
                    'response_hi': "डिस्क उपयोग:\n" + "\n".join(drives)}
        except Exception as e:
            return {'success': False, 'response': f"Disk info error: {e}"}
