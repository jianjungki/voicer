import platform
import os
import sys
from typing import Dict, Any, List

def get_system_font() -> str:
    """获取系统默认字体"""
    system = platform.system()
    if system == 'Windows':
        return "Microsoft YaHei"  # Windows 微软雅黑
    if system == 'Darwin':
        return "PingFang SC"  # macOS 苹方
    return "Sans"  # 其他系统

def is_windows() -> bool:
    """检查是否为 Windows 系统"""
    return platform.system() == 'Windows'

def is_macos() -> bool:
    """检查是否为 macOS 系统"""
    return platform.system() == 'Darwin'

def is_linux() -> bool:
    """检查是否为 Linux 系统"""
    return platform.system() == 'Linux'

def get_app_data_path() -> str:
    """获取应用数据路径"""
    system = platform.system()
    if system == 'Windows':
        return os.path.join(os.environ.get('APPDATA', ''), 'AudioSubtitle')
    if system == 'Darwin':
        return os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'AudioSubtitle')
    return os.path.join(os.path.expanduser('~'), '.audiosubtitle')

def ensure_dir_exists(path: str) -> None:
    """确保目录存在"""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def get_resource_path(relative_path: str) -> str:
    """获取资源文件路径"""
    # 如果是开发环境，直接返回相对路径
    if os.path.exists(os.path.join('audio_subtitle', 'resources')):
        return os.path.join('audio_subtitle', 'resources', relative_path)
    
    # 如果是打包环境，返回打包后的路径
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, 'resources', relative_path)

def get_window_list() -> List[Dict[str, Any]]:
    """获取窗口列表（兼容函数，建议使用 WindowManager 类）"""
    # 避免循环导入
    from ..core.window_manager import WindowManager
    manager = WindowManager()
    return manager.get_window_list()
