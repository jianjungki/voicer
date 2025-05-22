import platform
from typing import List, Dict, Any, Optional
from PySide6.QtCore import QObject, Signal

class WindowManager(QObject):
    """窗口管理器，负责获取系统窗口列表和窗口捕获"""
    
    # 定义信号
    window_list_updated = Signal(list)  # 窗口列表更新信号
    error_occurred = Signal(str)  # 错误信号
    
    def __init__(self):
        super().__init__()
        self.windows: List[Dict[str, Any]] = []
    
    def refresh_window_list(self) -> List[Dict[str, Any]]:
        """刷新窗口列表"""
        try:
            self.windows = self.get_window_list()
            self.window_list_updated.emit(self.windows)
            return self.windows
        except Exception as e:
            self.error_occurred.emit(f"Error refreshing window list: {e}")
            return []
    
    def get_window_list(self) -> List[Dict[str, Any]]:
        """获取窗口列表"""
        system = platform.system()
        if system == 'Windows':
            return self._get_windows_window_list()
        elif system == 'Darwin':  # macOS
            return self._get_macos_window_list()
        else:
            return self._get_default_window_list()
    
    def _get_windows_window_list(self) -> List[Dict[str, Any]]:
        """获取 Windows 窗口列表"""
        try:
            import win32gui
            import win32process
            processes = []
            
            def window_enumeration_handler(hwnd, ctx):
                if win32gui.IsWindowVisible(hwnd):
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        processes.append({'hwnd': hwnd, 'pid': pid, 'title': title})
            
            win32gui.EnumWindows(window_enumeration_handler, None)
            return processes
        except ImportError:
            self.error_occurred.emit("Warning: win32gui module not found")
            return self._get_default_window_list()
        except Exception as e:
            self.error_occurred.emit(f"Error getting Windows window list: {e}")
            return self._get_default_window_list()
    
    def _get_macos_window_list(self) -> List[Dict[str, Any]]:
        """获取 macOS 窗口列表"""
        try:
            import subprocess
            # 使用 AppleScript 获取所有窗口标题
            script = '''
            tell application "System Events"
                set windowList to {}
                repeat with proc in (every process whose background only is false)
                    set procName to name of proc
                    set windowList to windowList & {procName}
                end repeat
            end tell
            '''
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            if result.returncode == 0:
                titles = result.stdout.strip().split(', ')
                return [{'title': title, 'pid': 0, 'hwnd': None} for title in titles if title]
        except Exception as e:
            self.error_occurred.emit(f"Error getting macOS window list: {e}")
        
        return self._get_default_window_list()
    
    def _get_default_window_list(self) -> List[Dict[str, Any]]:
        """获取默认窗口列表"""
        return [{'title': 'System Audio', 'pid': 0, 'hwnd': None}]
    
    def get_window_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """根据标题获取窗口"""
        for window in self.windows:
            if window['title'] == title:
                return window
        return None
    
    def get_window_by_pid(self, pid: int) -> Optional[Dict[str, Any]]:
        """根据进程 ID 获取窗口"""
        for window in self.windows:
            if window['pid'] == pid:
                return window
        return None
    
    def get_window_by_hwnd(self, hwnd: int) -> Optional[Dict[str, Any]]:
        """根据窗口句柄获取窗口"""
        for window in self.windows:
            if window['hwnd'] == hwnd:
                return window
        return None