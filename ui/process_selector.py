from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget,
                                    QListWidgetItem, QPushButton, QLabel)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon, QFont
import os

class ProcessSelector(QDialog):
    """进程选择器对话框，用于选择要捕获的窗口/进程"""
    
    # 定义信号
    process_selected = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.processes = []
        self.setup_ui()
    
    def setup_ui(self):
        """创建 UI 组件"""
        # 设置窗口属性
        self.setWindowTitle("选择程序")
        self.setMinimumSize(400, 500)
        # 移除帮助按钮
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # 创建主布局
        layout = QVBoxLayout(self)
        
        # 创建提示标签
        label = QLabel("请选择要捕获的窗口：")
        label.setFont(QFont(label.font().family(), 10))
        layout.addWidget(label)
        
        # 创建列表部件
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.list_widget)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 创建刷新按钮
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.clicked.connect(self.refresh_process_list)
        button_layout.addWidget(self.refresh_button)
        
        # 添加弹性空间
        button_layout.addStretch()
        
        # 创建确定和取消按钮
        self.select_button = QPushButton("选择")
        self.select_button.setDefault(True)
        self.select_button.clicked.connect(self.accept)
        button_layout.addWidget(self.select_button)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        # 添加按钮布局
        layout.addLayout(button_layout)
    
    def refresh_process_list(self):
        """刷新进程列表"""
        # 清空列表
        self.list_widget.clear()
        
        # 获取窗口列表
        from ..core.window_manager import WindowManager
        window_manager = WindowManager()
        self.processes = window_manager.get_window_list()
        
        # 添加到列表部件
        for proc in self.processes:
            title = proc.get('title', '')
            if title:
                item = QListWidgetItem(title)
                self.list_widget.addItem(item)
        
        # 如果有项目，选中第一项
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)
    
    def showEvent(self, event):
        """窗口显示事件"""
        super().showEvent(event)
        # 显示时刷新进程列表
        self.refresh_process_list()
    
    def get_selected_process(self):
        """获取选中的进程信息"""
        current_row = self.list_widget.currentRow()
        if current_row >= 0 and current_row < len(self.processes):
            return self.processes[current_row]
        return None
    
    def accept(self):
        """确定按钮点击事件"""
        selected_process = self.get_selected_process()
        if selected_process:
            self.process_selected.emit(selected_process)
            super().accept()