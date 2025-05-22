from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget , QMenu, QMenuBar
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QIcon, QKeySequence, QAction

from ..ui.subtitle_bar import SubtitleBar
from ..ui.process_selector import ProcessSelector
from ..ui.settings_dialog import SettingsDialog
from ..ui.theme_manager import ThemeManager
from ..core.audio_processor import AudioProcessor
from ..core.speech_recognition import SpeechRecognizer
from ..utils.tray_manager import TrayManager
from ..utils.system_utils import get_resource_path

import os

class MainWindow(QMainWindow):
    """主窗口类，管理应用程序的主要功能和界面"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.subtitle_bar = None
        self.selected_process = None
        
        # 创建组件
        self.setup_components()
        
        # 创建 UI
        self.setup_ui()
        
        # 连接信号和槽
        self.connect_signals()
        
        # 应用设置
        self.apply_settings()
    
    def setup_components(self):
        """创建应用程序组件"""
        # 创建主题管理器
        self.theme_manager = ThemeManager(self.config)
        
        # 创建音频处理器
        self.audio_processor = AudioProcessor(self.config)
        
        # 创建语音识别器
        self.speech_recognizer = SpeechRecognizer(self.config)
        
        # 创建系统托盘
        self.tray_manager = TrayManager(self)
    
    def setup_ui(self):
        """创建 UI 组件"""
        # 设置窗口属性
        self.setWindowTitle("实时字幕")
        self.resize(400, 300)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 创建菜单栏
        self.create_menu_bar()
    
    def create_menu_bar(self):
        """创建菜单栏"""
        # 文件菜单
        file_menu = self.menuBar().addMenu("文件")
        
        # 选择程序动作
        select_process_action = QAction("选择程序", self)
        select_process_action.triggered.connect(self.show_process_selector)
        file_menu.addAction(select_process_action)
        
        file_menu.addSeparator()
        
        # 退出动作
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 视图菜单
        view_menu = self.menuBar().addMenu("视图")
        
        # 显示/隐藏字幕条动作
        self.show_subtitle_action = QAction("显示字幕条", self)
        self.show_subtitle_action.setCheckable(True)
        self.show_subtitle_action.setChecked(True)
        self.show_subtitle_action.triggered.connect(self.toggle_subtitle_bar)
        view_menu.addAction(self.show_subtitle_action)
        
        # 置顶动作
        self.stay_on_top_action = QAction("保持窗口置顶", self)
        self.stay_on_top_action.setCheckable(True)
        self.stay_on_top_action.setChecked(self.config.get("stay_on_top", False))
        self.stay_on_top_action.triggered.connect(self.toggle_stay_on_top)
        view_menu.addAction(self.stay_on_top_action)

        # 调试模式动作
        self.debug_mode_action = QAction("调试模式", self)
        self.debug_mode_action.setCheckable(True)
        self.debug_mode_action.setChecked(False)
        self.debug_mode_action.triggered.connect(self.toggle_debug_mode)
        view_menu.addAction(self.debug_mode_action)
        
        view_menu.addSeparator()
        
        # 主题菜单
        theme_menu = view_menu.addMenu("主题")
        
        # 浅色主题动作
        light_theme_action = QAction("浅色", self)
        light_theme_action.triggered.connect(lambda: self.theme_manager.apply_theme("浅色"))
        theme_menu.addAction(light_theme_action)
        
        # 深色主题动作
        dark_theme_action = QAction("深色", self)
        dark_theme_action.triggered.connect(lambda: self.theme_manager.apply_theme("深色"))
        theme_menu.addAction(dark_theme_action)
        
        # 工具菜单
        tools_menu = self.menuBar().addMenu("工具")
        
        # 设置动作
        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
    
    def connect_signals(self):
        """连接信号和槽"""
        # 音频处理器信号
        self.audio_processor.audio_frame_ready.connect(self.speech_recognizer.process_audio_frame)
        
        # 语音识别器信号
        self.speech_recognizer.text_recognized.connect(self.update_subtitle)
        
        # 系统托盘信号
        self.tray_manager.show_requested.connect(self.show)
        self.tray_manager.hide_requested.connect(self.hide)
        self.tray_manager.settings_requested.connect(self.show_settings)
        self.tray_manager.quit_requested.connect(self.close)
        self.tray_manager.stay_on_top_changed.connect(self.set_stay_on_top)
    
    def apply_settings(self):
        """应用设置"""
        # 应用主题
        self.theme_manager.apply_theme()
        
        # 设置窗口置顶
        self.set_stay_on_top(self.config.get("stay_on_top", False))
        
        # 如果配置了自动启动，则启动识别
        if self.config.get("auto_start", True):
            self.start_recognition()
    
    def show_process_selector(self):
        """显示进程选择器对话框"""
        selector = ProcessSelector(self)
        selector.process_selected.connect(self.on_process_selected)
        selector.exec()
    
    def on_process_selected(self, process):
        """处理进程选择事件"""
        self.selected_process = process
        print(f"Selected process: {process['title']}")
        
        # 如果字幕条已经存在，则更新标题
        if self.subtitle_bar:
            self.subtitle_bar.setWindowTitle(f"实时字幕 - {process['title']}")
        
        # 启动识别
        self.start_recognition()
    
    def toggle_subtitle_bar(self, checked):
        """切换字幕条显示状态"""
        if checked:
            self.show_subtitle_bar()
        else:
            self.hide_subtitle_bar()
    
    def show_subtitle_bar(self):
        """显示字幕条"""
        if not self.subtitle_bar:
            self.subtitle_bar = SubtitleBar(self.config)
            self.subtitle_bar.closed.connect(self.on_subtitle_bar_closed)
            # 设置初始调试模式状态
            if hasattr(self, 'debug_mode_action'):
                self.subtitle_bar.debug_mode = self.debug_mode_action.isChecked()
        
        self.subtitle_bar.show()
        self.show_subtitle_action.setChecked(True)
    
    def hide_subtitle_bar(self):
        """隐藏字幕条"""
        if self.subtitle_bar:
            self.subtitle_bar.hide()
        self.show_subtitle_action.setChecked(False)
    
    def on_subtitle_bar_closed(self):
        """处理字幕条关闭事件"""
        self.show_subtitle_action.setChecked(False)
    
    def toggle_stay_on_top(self, checked):
        """切换窗口置顶状态"""
        self.set_stay_on_top(checked)
        self.config.set("stay_on_top", checked)
    
    def set_stay_on_top(self, stay_on_top):
        """设置窗口置顶"""
        self.stay_on_top_action.setChecked(stay_on_top)
        
        # 更新系统托盘
        self.tray_manager.update_stay_on_top_state(stay_on_top)
        
        # 更新字幕条
        if self.subtitle_bar:
            self.subtitle_bar.set_stay_on_top(stay_on_top)
    
    def show_settings(self):
        """显示设置对话框"""
        settings_dialog = SettingsDialog(self.config, self)
        settings_dialog.settings_changed.connect(self.on_settings_changed)
        settings_dialog.exec()
    
    def on_settings_changed(self, settings):
        """处理设置更改事件"""
        # 更新配置
        self.config.update(settings)
        
        # 应用主题
        if self.theme_manager.current_theme != settings["theme"]:
            self.theme_manager.apply_theme(settings["theme"])
        
        # 更新字幕条
        if self.subtitle_bar:
            self.subtitle_bar.update_config()
        
        # 更新窗口置顶状态
        self.set_stay_on_top(settings["stay_on_top"])
        
        # 更新音频处理器配置
        self.audio_processor.update_config()
    
    def toggle_debug_mode(self, checked):
        """切换调试模式"""
        if self.subtitle_bar:
            is_debug = self.subtitle_bar.toggle_debug_mode()
            self.debug_mode_action.setChecked(is_debug)
            
    def start_recognition(self):
        """启动语音识别"""
        self.speech_recognizer.start()
        self.audio_processor.start()
        
        # 显示字幕条
        self.show_subtitle_bar()
    
    def stop_recognition(self):
        """停止语音识别"""
        self.audio_processor.stop()
        self.speech_recognizer.stop()
    
    @Slot(str)
    def update_subtitle(self, text):
        """更新字幕"""
        if self.subtitle_bar:
            # 使用默认值False，因为现在我们不再接收is_sentence_end参数
            self.subtitle_bar.update_subtitle(text, False)
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 停止语音识别
        self.stop_recognition()
        
        # 清理系统托盘
        self.tray_manager.cleanup()
        
        # 接受关闭事件
        event.accept()