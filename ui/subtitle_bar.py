from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PySide6.QtCore import (
    Qt,
    Signal,
    QPoint,
    QSize
)
from PySide6.QtGui import QFont, QColor, QPalette, QTextCursor
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTextEdit

class SubtitleBar(QWidget):
    """字幕条组件，显示实时字幕"""
    
    # 定义信号
    closed = Signal()
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.drag_position = None  # 初始化拖动位置变量
        self.debug_mode = False  # 调试模式标志
        
        # 设置窗口属性
        self.setup_window()
        
        # 创建 UI 组件
        self.setup_ui()
        
        # 应用样式
        self.apply_style()
    
    def setup_window(self):
        """设置窗口属性"""
        # 无边框窗口
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint |
                          Qt.WindowType.WindowStaysOnTopHint |
                          Qt.WindowType.Tool)
        
        # 设置窗口透明
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 设置窗口大小
        self.resize(700, 120)
        
        # 居中显示
        self.center_on_screen()
    
    def setup_ui(self):
        """创建 UI 组件"""
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建文本编辑器
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        
        # 添加到布局
        layout.addWidget(self.text_edit)
    
    def apply_style(self):
        """应用样式"""
        # 设置窗口透明度
        opacity = self.config.get("opacity", 0.8)
        self.setWindowOpacity(opacity)
        
        # 设置字体
        font_family = self.config.get("font_family", "Microsoft YaHei")
        font_size = self.config.get("font_size", 15)
        font = QFont(font_family, font_size)
        self.text_edit.setFont(font)
        
        # 设置颜色
        text_color = self.config.get("text_color", "#FFFFFF")
        bg_color = self.config.get("bg_color", "#000000")
        highlight_color = self.config.get("highlight_color", "#FFFF00")
        
        # 设置文本编辑器样式
        self.text_edit.setStyleSheet(f"""
            QTextEdit {{
                color: {text_color};
                background-color: {bg_color};
                border: none;
                border-radius: 10px;
                padding: 10px;
            }}
        """)
        
        # 保存高亮颜色
        self.highlight_color = QColor(highlight_color)
    
    def update_subtitle(self, text, is_sentence_end=False):
        """更新字幕文本"""
        print(f"Updating subtitle: text='{text}', is_sentence_end={is_sentence_end}")
        print(f"Current text before update: '{self.text_edit.toPlainText()}'")
        
        # 启用文本编辑
        self.text_edit.setReadOnly(False)
        
        # 如果处于调试模式，显示调试信息
        if self.debug_mode:
            display_text = f"[识别文本: '{text}' | 句尾: {is_sentence_end}]"
        else:
            display_text = text
            
        # 替换文本并设置颜色
        self.text_edit.clear()
        cursor = self.text_edit.textCursor()
        format = cursor.charFormat()
        format.setForeground(self.highlight_color)
        cursor.setCharFormat(format)
        cursor.insertText(display_text)
        
        # 自动滚动到最新内容
        self.text_edit.setTextCursor(cursor)
        self.text_edit.ensureCursorVisible()
        
        print(f"Current text after update: '{self.text_edit.toPlainText()}'")
        
        # 禁用文本编辑
        self.text_edit.setReadOnly(True)
    
    def center_on_screen(self):
        """将窗口居中显示"""
        screen_geometry = self.screen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
    
    def set_stay_on_top(self, stay_on_top):
        """设置窗口是否置顶"""
        flags = self.windowFlags()
        if stay_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()  # 需要重新显示窗口以应用新的标志
    
    def update_config(self):
        """更新配置"""
        self.apply_style()
    
    def toggle_debug_mode(self):
        """切换调试模式"""
        self.debug_mode = not self.debug_mode
        return self.debug_mode
    
    # 鼠标事件处理，用于窗口拖动
    def mousePressEvent(self, event):
        """鼠标按下事件，记录拖动起始位置"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 兼容不同版本的 PySide6
            try:
                # 新版本 PySide6
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            except AttributeError:
                # 旧版本 PySide6
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件，实现窗口拖动"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None:
            try:
                # 新版本 PySide6
                new_pos = event.globalPosition().toPoint() - self.drag_position
            except AttributeError:
                # 旧版本 PySide6
                new_pos = event.globalPos() - self.drag_position
            self.move(new_pos)
            event.accept()
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        self.closed.emit()
        event.accept()