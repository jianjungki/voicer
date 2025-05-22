import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal
from ..utils.system_utils import get_resource_path

class ThemeManager(QObject):
    """主题管理器，负责管理应用程序主题"""
    
    # 定义信号
    theme_changed = Signal(str)  # 主题变更信号
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.current_theme = config.get("theme", "浅色")
        
        # 加载主题
        self.apply_theme(self.current_theme)
    
    def apply_theme(self, theme_name=None):
        """应用主题"""
        if theme_name is None:
            theme_name = self.current_theme
        else:
            self.current_theme = theme_name
            self.config.set("theme", theme_name)
        
        # 加载样式表
        style_file = self._get_style_file(theme_name)
        
        # 如果样式文件存在，则应用样式
        if os.path.exists(style_file):
            with open(style_file, "r", encoding="utf-8") as f:
                style = f.read()
                QApplication.instance().setStyleSheet(style)
        
        # 发出主题已变更信号
        self.theme_changed.emit(theme_name)
    
    def _get_style_file(self, theme_name):
        """获取样式文件路径"""
        if theme_name == "深色":
            return get_resource_path(os.path.join("styles", "dark.qss"))
        return get_resource_path(os.path.join("styles", "light.qss"))
    
    def toggle_theme(self):
        """切换主题"""
        if self.current_theme == "浅色":
            self.apply_theme("深色")
        else:
            self.apply_theme("浅色")
    
    def get_theme_color(self, key, default=None):
        """获取主题颜色"""
        # 根据当前主题返回对应的颜色
        colors = {
            "浅色": {
                "text": "#000000",
                "background": "#FFFFFF",
                "highlight": "#007BFF",
                "border": "#CCCCCC",
                "button": "#F0F0F0",
                "button_hover": "#E0E0E0",
                "button_pressed": "#D0D0D0",
            },
            "深色": {
                "text": "#FFFFFF",
                "background": "#2D2D30",
                "highlight": "#0078D7",
                "border": "#3F3F46",
                "button": "#3F3F46",
                "button_hover": "#505050",
                "button_pressed": "#606060",
            }
        }
        
        theme_colors = colors.get(self.current_theme, colors["浅色"])
        return theme_colors.get(key, default)
