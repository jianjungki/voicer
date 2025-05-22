import os
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QObject, Signal

from ..utils.system_utils import get_resource_path, is_macos

class TrayManager(QObject):
    """系统托盘管理器"""
    
    # 定义信号
    show_requested = Signal()
    hide_requested = Signal()
    settings_requested = Signal()
    quit_requested = Signal()
    stay_on_top_changed = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tray_icon = None
        self.stay_on_top = False
        self.stay_on_top_action = None
        
        # macOS 下不使用系统托盘
        if not is_macos():
            self.setup_tray()
    
    def setup_tray(self):
        """设置系统托盘"""
        if self.tray_icon is not None:
            return
            
        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon(self.parent())
        
        # 设置图标
        icon_path = get_resource_path(os.path.join('../icons', 'app.png'))
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        
        # 设置工具提示
        self.tray_icon.setToolTip("实时字幕")
        
        # 创建托盘菜单
        self.create_tray_menu()
        
        # 连接信号
        self.tray_icon.activated.connect(self._on_tray_activated)
        
        # 显示图标
        self.tray_icon.show()
    
    def create_tray_menu(self):
        """创建托盘菜单"""
        menu = QMenu()
        
        # 显示/隐藏动作
        show_action = QAction("显示", self)
        show_action.triggered.connect(self.show_requested.emit)
        menu.addAction(show_action)
        
        hide_action = QAction("隐藏", self)
        hide_action.triggered.connect(self.hide_requested.emit)
        menu.addAction(hide_action)
        
        menu.addSeparator()
        
        # 置顶动作
        self.stay_on_top_action = QAction("保持窗口置顶", self)
        self.stay_on_top_action.setCheckable(True)
        self.stay_on_top_action.setChecked(self.stay_on_top)
        self.stay_on_top_action.triggered.connect(self._on_stay_on_top_triggered)
        menu.addAction(self.stay_on_top_action)
        
        menu.addSeparator()
        
        # 设置动作
        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self.settings_requested.emit)
        menu.addAction(settings_action)
        
        menu.addSeparator()
        
        # 退出动作
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.quit_requested.emit)
        menu.addAction(quit_action)
        
        # 设置菜单
        self.tray_icon.setContextMenu(menu)
    
    def _on_tray_activated(self, reason):
        """处理托盘图标激活事件"""
        # 在 Windows 上，双击显示窗口
        # 在其他系统上，单击显示窗口
        if ((reason == QSystemTrayIcon.DoubleClick and os.name == 'nt') or
            (reason == QSystemTrayIcon.Trigger and os.name != 'nt')):
            self.show_requested.emit()
    
    def _on_stay_on_top_triggered(self, checked):
        """处理置顶状态改变事件"""
        self.stay_on_top = checked
        self.stay_on_top_changed.emit(checked)
    
    def update_stay_on_top_state(self, state):
        """更新置顶状态"""
        self.stay_on_top = state
        if self.tray_icon is not None:
            self.stay_on_top_action.setChecked(state)
    
    def show_message(self, title, message, icon=QSystemTrayIcon.Information):
        """显示托盘通知消息"""
        if self.tray_icon is not None:
            self.tray_icon.showMessage(title, message, icon)
    
    def cleanup(self):
        """清理资源"""
        if self.tray_icon is not None:
            self.tray_icon.hide()
            self.tray_icon = None
            