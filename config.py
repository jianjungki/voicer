import json
import os

class Config:
    """配置管理类，用于管理应用程序配置"""
    
    def __init__(self, config_file=None):
        self.config_file = config_file or "config.json"
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置"""
        default_config = {
            # 一般设置
            "theme": "浅色",  # 主题：浅色/深色
            "opacity": 0.8,  # 透明度：0.1-1.0
            "stay_on_top": False,  # 窗口置顶
            "auto_start": True,  # 自动启动识别
            
            # 字幕设置
            "font_family": "",  # 字体，空字符串表示使用系统默认字体
            "font_size": 15,  # 字体大小
            "text_color": "#FFFFFF",  # 文本颜色
            "bg_color": "#000000",  # 背景颜色
            "highlight_color": "#FFFF00",  # 高亮颜色
            
            # 音频设置
            "silence_threshold": 300,  # 静音阈值
            "max_silence_duration": 2.0,  # 最大静音持续时间（秒）
            
            # API 设置
            "api_key": "sk-4eb7202bb9a64793a34365a86b2de5a3",  # API 密钥
        }
        
        # 如果配置文件存在则加载
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    # 更新默认配置
                    default_config.update(loaded_config)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
        
        return default_config
    
    def save_config(self):
        """保存配置"""
        try:
            # 确保配置文件目录存在
            os.makedirs(os.path.dirname(os.path.abspath(self.config_file)), exist_ok=True)
            
            # 保存配置
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get(self, key, default=None):
        """获取配置项"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """设置配置项"""
        self.config[key] = value
        self.save_config()
    
    def update(self, config_dict):
        """批量更新配置"""
        self.config.update(config_dict)
        self.save_config()