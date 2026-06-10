"""ARIA Skills Package"""
from .system_control import SystemControl
from .office_tasks import OfficeTasks
from .web_tasks import WebTasks
from .media_control import MediaControl
from .home_control import HomeControl
from .information import Information
from .file_manager import FileManager
from .communication import Communication

__all__ = [
    'SystemControl', 'OfficeTasks', 'WebTasks', 'MediaControl',
    'HomeControl', 'Information', 'FileManager', 'Communication'
]
