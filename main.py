import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from .ui.main_window import MainWindow
from .config import Config
from .utils.system_utils import get_app_data_path, ensure_dir_exists, get_resource_path

def main():
    """主程序入口"""
    # 确保应用数据目录存在
    app_data_path = get_app_data_path()
    ensure_dir_exists(app_data_path)

    # 创建应用实例
    app = QApplication(sys.argv)
    app.setApplicationName("实时字幕")

    # 加载应用图标
    icon_path = get_resource_path(os.path.join('icons', 'app.png'))
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # 加载配置
    config = Config(os.path.join(app_data_path, 'config.json'))

    # 创建并显示主窗口
    window = MainWindow(config)
    window.show()

    # 运行应用程序
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
