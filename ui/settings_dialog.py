from PySide6.QtWidgets import (QDialog, QTabWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                                    QComboBox, QSlider, QPushButton, QColorDialog, QLabel,
                                    QSpinBox, QCheckBox, QGroupBox, QWidget)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor, QFont

class SettingsDialog(QDialog):
    """设置对话框，用于配置应用程序设置"""
    
    # 定义信号
    settings_changed = Signal(dict)
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """创建 UI 组件"""
        # 设置窗口属性
        self.setWindowTitle("设置")
        self.resize(500, 400)
        
        # 创建主布局
        layout = QVBoxLayout(self)
        
        # 创建选项卡部件
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 创建外观选项卡
        self.create_appearance_tab()
        
        # 创建语音识别选项卡
        self.create_recognition_tab()
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 添加弹性空间
        button_layout.addStretch()
        
        # 创建确定和取消按钮
        self.ok_button = QPushButton("确定")
        self.ok_button.setDefault(True)
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        # 添加按钮布局
        layout.addLayout(button_layout)
    
    def create_appearance_tab(self):
        """创建外观选项卡"""
        appearance_widget = QWidget()
        appearance_layout = QVBoxLayout(appearance_widget)
        
        # 创建主题设置组
        theme_group = QGroupBox("主题设置")
        theme_layout = QFormLayout(theme_group)
        
        # 主题选择
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["浅色", "深色", "跟随系统"])
        theme_layout.addRow("主题:", self.theme_combo)
        
        # 透明度滑块
        self.opacity_slider = QSlider()
        self.opacity_slider.setOrientation(Qt.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setTickPosition(QSlider.TicksBelow)
        self.opacity_slider.setTickInterval(10)
        
        # 添加透明度值标签
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(self.opacity_slider)
        self.opacity_label = QLabel("80%")
        opacity_layout.addWidget(self.opacity_label)
        
        # 连接透明度滑块信号
        self.opacity_slider.valueChanged.connect(self.update_opacity_label)
        
        theme_layout.addRow("透明度:", opacity_layout)
        
        appearance_layout.addWidget(theme_group)
        
        # 创建字体设置组
        font_group = QGroupBox("字体设置")
        font_layout = QFormLayout(font_group)
        
        # 字体大小
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 36)
        font_layout.addRow("字体大小:", self.font_size_spin)
        
        appearance_layout.addWidget(font_group)
        
        # 创建颜色设置组
        color_group = QGroupBox("颜色设置")
        color_layout = QFormLayout(color_group)
        
        # 文本颜色选择
        self.text_color_button = QPushButton()
        self.text_color_button.setFixedSize(60, 30)
        self.text_color_button.clicked.connect(self.choose_text_color)
        color_layout.addRow("文本颜色:", self.text_color_button)
        
        # 背景颜色选择
        self.bg_color_button = QPushButton()
        self.bg_color_button.setFixedSize(60, 30)
        self.bg_color_button.clicked.connect(self.choose_bg_color)
        color_layout.addRow("背景颜色:", self.bg_color_button)
        
        # 高亮颜色选择
        self.highlight_color_button = QPushButton()
        self.highlight_color_button.setFixedSize(60, 30)
        self.highlight_color_button.clicked.connect(self.choose_highlight_color)
        color_layout.addRow("高亮颜色:", self.highlight_color_button)
        
        appearance_layout.addWidget(color_group)
        
        # 添加弹性空间
        appearance_layout.addStretch()
        
        # 添加到选项卡
        self.tab_widget.addTab(appearance_widget, "外观")
    
    def create_recognition_tab(self):
        """创建语音识别选项卡"""
        recognition_widget = QWidget()
        recognition_layout = QVBoxLayout(recognition_widget)
        
        # 创建基本设置组
        basic_group = QGroupBox("基本设置")
        basic_layout = QFormLayout(basic_group)
        
        # 自动启动识别
        self.auto_start_check = QCheckBox()
        basic_layout.addRow("自动启动识别:", self.auto_start_check)
        
        # 保持窗口置顶
        self.stay_on_top_check = QCheckBox()
        basic_layout.addRow("保持窗口置顶:", self.stay_on_top_check)
        
        recognition_layout.addWidget(basic_group)
        
        # 创建高级设置组
        advanced_group = QGroupBox("高级设置")
        advanced_layout = QFormLayout(advanced_group)
        
        # 静音阈值
        self.silence_threshold_slider = QSlider()
        self.silence_threshold_slider.setOrientation(Qt.Horizontal)
        self.silence_threshold_slider.setRange(100, 1000)
        self.silence_threshold_slider.setTickPosition(QSlider.TicksBelow)
        self.silence_threshold_slider.setTickInterval(100)
        
        # 添加静音阈值标签
        silence_layout = QHBoxLayout()
        silence_layout.addWidget(self.silence_threshold_slider)
        self.silence_threshold_label = QLabel("300")
        silence_layout.addWidget(self.silence_threshold_label)
        
        # 连接静音阈值滑块信号
        self.silence_threshold_slider.valueChanged.connect(self.update_silence_threshold_label)
        
        advanced_layout.addRow("静音阈值:", silence_layout)
        
        # 静音持续时间
        self.silence_duration_spin = QSpinBox()
        self.silence_duration_spin.setRange(1, 10)
        self.silence_duration_spin.setSuffix(" 秒")
        advanced_layout.addRow("静音持续时间:", self.silence_duration_spin)
        
        # API Key 设置
        self.api_key_label = QLabel("sk-4eb7202bb9a64793a34365a86b2de5a3")
        self.api_key_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        advanced_layout.addRow("API Key:", self.api_key_label)
        
        recognition_layout.addWidget(advanced_group)
        
        # 添加弹性空间
        recognition_layout.addStretch()
        
        # 添加到选项卡
        self.tab_widget.addTab(recognition_widget, "语音识别")
    
    def load_settings(self):
        """加载设置"""
        # 加载主题设置
        theme = self.config.get("theme", "浅色")
        if theme == "浅色":
            self.theme_combo.setCurrentIndex(0)
        elif theme == "深色":
            self.theme_combo.setCurrentIndex(1)
        else:
            self.theme_combo.setCurrentIndex(2)
        
        # 加载透明度设置
        opacity = self.config.get("opacity", 0.8)
        self.opacity_slider.setValue(int(opacity * 100))
        self.update_opacity_label(int(opacity * 100))
        
        # 加载字体设置
        font_size = self.config.get("font_size", 15)
        self.font_size_spin.setValue(font_size)
        
        # 加载颜色设置
        text_color = self.config.get("text_color", "#FFFFFF")
        bg_color = self.config.get("bg_color", "#000000")
        highlight_color = self.config.get("highlight_color", "#FFFF00")
        
        self.text_color = QColor(text_color)
        self.bg_color = QColor(bg_color)
        self.highlight_color = QColor(highlight_color)
        
        self.text_color_button.setStyleSheet(f"background-color: {text_color};")
        self.bg_color_button.setStyleSheet(f"background-color: {bg_color};")
        self.highlight_color_button.setStyleSheet(f"background-color: {highlight_color};")
        
        # 加载语音识别设置
        auto_start = self.config.get("auto_start", True)
        self.auto_start_check.setChecked(auto_start)
        
        stay_on_top = self.config.get("stay_on_top", False)
        self.stay_on_top_check.setChecked(stay_on_top)
        
        silence_threshold = self.config.get("silence_threshold", 300)
        self.silence_threshold_slider.setValue(silence_threshold)
        self.update_silence_threshold_label(silence_threshold)
        
        max_silence_duration = self.config.get("max_silence_duration", 2.0)
        self.silence_duration_spin.setValue(int(max_silence_duration))
        
        api_key = self.config.get("api_key", "sk-4eb7202bb9a64793a34365a86b2de5a3")
        self.api_key_label.setText(api_key)
    
    def update_opacity_label(self, value):
        """更新透明度标签"""
        self.opacity_label.setText(f"{value}%")
    
    def update_silence_threshold_label(self, value):
        """更新静音阈值标签"""
        self.silence_threshold_label.setText(str(value))
    
    def choose_text_color(self):
        """选择文本颜色"""
        color = QColorDialog.getColor(self.text_color, self, "选择文本颜色")
        if color.isValid():
            self.text_color = color
            self.text_color_button.setStyleSheet(f"background-color: {color.name()};")
    
    def choose_bg_color(self):
        """选择背景颜色"""
        color = QColorDialog.getColor(self.bg_color, self, "选择背景颜色")
        if color.isValid():
            self.bg_color = color
            self.bg_color_button.setStyleSheet(f"background-color: {color.name()};")
    
    def choose_highlight_color(self):
        """选择高亮颜色"""
        color = QColorDialog.getColor(self.highlight_color, self, "选择高亮颜色")
        if color.isValid():
            self.highlight_color = color
            self.highlight_color_button.setStyleSheet(f"background-color: {color.name()};")
    
    def accept(self):
        """确定按钮点击事件"""
        # 收集设置
        settings = {
            "theme": self.theme_combo.currentText(),
            "opacity": self.opacity_slider.value() / 100,
            "font_size": self.font_size_spin.value(),
            "text_color": self.text_color.name(),
            "bg_color": self.bg_color.name(),
            "highlight_color": self.highlight_color.name(),
            "auto_start": self.auto_start_check.isChecked(),
            "stay_on_top": self.stay_on_top_check.isChecked(),
            "silence_threshold": self.silence_threshold_slider.value(),
            "max_silence_duration": self.silence_duration_spin.value(),
            "api_key": self.api_key_label.text()
        }
        
        # 发出设置已更改信号
        self.settings_changed.emit(settings)
        
        # 调用父类的 accept 方法
        super().accept()