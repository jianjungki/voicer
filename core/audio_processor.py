import time
from typing import Optional
import audioop
import pyaudio
from PySide6.QtCore import QObject, Signal, QThread

class AudioProcessorThread(QThread):
    """音频处理线程，负责读取和处理音频数据"""
    
    # 定义信号
    audio_frame_ready = Signal(bytes)
    silence_detected = Signal(bool)
    error_occurred = Signal(str)
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.mic: Optional[pyaudio.PyAudio] = None
        self.stream: Optional[pyaudio.Stream] = None
        self.is_running = False
        self.is_silent = False
        
        # 静音检测相关变量
        self.silence_threshold = config.get("silence_threshold", 300)
        self.max_silence_duration = config.get("max_silence_duration", 2.0)
        self.silence_duration = 0
        self.last_active_time = time.time()
    
    def run(self):
        """线程运行函数，处理音频数据"""
        self.start_audio()
        while self.is_running:
            self.process_audio_frame()
            # 短暂休眠以减少 CPU 使用
            time.sleep(0.01)
        self.stop_audio()
    
    def start_audio(self):
        """启动音频处理"""
        try:
            self.mic = pyaudio.PyAudio()
            self.stream = self.mic.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=3200
            )
            self.is_running = True
        except Exception as e:
            self.error_occurred.emit(f"Error starting audio processor: {e}")
    
    def stop_audio(self):
        """停止音频处理"""
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception as e:
                self.error_occurred.emit(f"Error closing audio stream: {e}")
        
        if self.mic:
            try:
                self.mic.terminate()
            except Exception as e:
                self.error_occurred.emit(f"Error terminating PyAudio: {e}")
        
        self.stream = None
        self.mic = None
    
    def process_audio_frame(self):
        """处理单个音频帧"""
        try:
            if not self.stream:
                return
            
            # 读取音频数据
            audio_data = self.stream.read(3200, exception_on_overflow=False)
            
            # 检测是否为静音
            current_is_silent = self.is_audio_silent(audio_data)
            
            if current_is_silent:
                self.silence_duration = time.time() - self.last_active_time
                
                # 如果静音时间超过阈值，发出信号
                if self.silence_duration > self.max_silence_duration and not self.is_silent:
                    self.is_silent = True
                    self.silence_detected.emit(True)
            else:
                # 检测到声音，重置静音计时器
                self.last_active_time = time.time()
                
                # 如果之前是静音状态，现在重新激活
                if self.is_silent:
                    self.is_silent = False
                    self.silence_detected.emit(False)
            
            # 发出音频帧信号
            if not self.is_silent:
                self.audio_frame_ready.emit(audio_data)
                
        except Exception as e:
            self.error_occurred.emit(f"Error processing audio: {e}")
    
    def is_audio_silent(self, audio_data: bytes) -> bool:
        """检测音频是否为静音"""
        try:
            # 使用 audioop 计算音频的 RMS 值，表示音频的平均能量
            rms = audioop.rms(audio_data, 2)  # 2表示每个样本是2字节
            return rms < self.silence_threshold
        except Exception as e:
            self.error_occurred.emit(f"Error checking audio silence: {e}")
            return False
    
    def update_config(self):
        """更新配置"""
        self.silence_threshold = self.config.get("silence_threshold", 300)
        self.max_silence_duration = self.config.get("max_silence_duration", 2.0)


class AudioProcessor(QObject):
    """音频处理器，管理音频处理线程"""
    
    # 转发线程的信号
    audio_frame_ready = Signal(bytes)
    silence_detected = Signal(bool)
    error_occurred = Signal(str)
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self._thread = AudioProcessorThread(self.config)  # 直接创建线程
        
        # 连接线程信号
        self._thread.audio_frame_ready.connect(self.audio_frame_ready)
        self._thread.silence_detected.connect(self.silence_detected)
        self._thread.error_occurred.connect(self.error_occurred)
    
    def start(self):
        """启动音频处理"""
        if not self._thread.isRunning():
            self._thread.is_running = True
            self._thread.start()
    
    def stop(self):
        """停止音频处理"""
        if self._thread.isRunning():
            self._thread.is_running = False
            self._thread.wait()
    
    def update_config(self):
        """更新配置"""
        self._thread.update_config()
        