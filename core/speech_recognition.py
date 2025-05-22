import os
from typing import Optional, Callable
from PySide6.QtCore import QObject, Signal, Slot
import dashscope
from dashscope.audio.asr import Recognition, RecognitionCallback, RecognitionResult

class SpeechRecognizer(QObject):
    """语音识别器类，处理实时语音识别"""
    
    # 定义信号
    text_recognized = Signal(str, bool)  # 识别到的文本和是否句子结束
    recognition_started = Signal()
    recognition_stopped = Signal()
    error_occurred = Signal(str)  # 错误信息

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.recognition: Optional[Recognition] = None
        self.callback: Optional[RecognitionCallback] = None
        self.is_running = False
        
        # 初始化 DashScope API key
        self._init_dashscope_api_key()

    def _init_dashscope_api_key(self) -> None:
        """初始化 DashScope API key"""
        api_key = self.config.get("api_key")
        if api_key:
            dashscope.api_key = api_key
        elif 'DASHSCOPE_API_KEY' in os.environ:
            dashscope.api_key = os.environ['DASHSCOPE_API_KEY']
        else:
            # 使用默认的 API key，建议在实际使用时替换为自己的 key
            dashscope.api_key = 'sk-4eb7202bb9a64793a34365a86b2de5a3'

    def start(self) -> None:
        """启动语音识别"""
        if self.is_running:
            return

        class Callback(RecognitionCallback):
            def __init__(self, recognizer):
                self.recognizer = recognizer

            def on_open(self) -> None:
                self.recognizer.recognition_started.emit()

            def on_close(self) -> None:
                self.recognizer.recognition_stopped.emit()

            def on_error(self, result: RecognitionResult) -> None:
                if hasattr(result, 'message'):
                    self.recognizer.error_occurred.emit(result.message)

            def on_event(self, result: RecognitionResult) -> None:
                try:
                    sentence = result.get_sentence()
                    if isinstance(sentence, dict) and 'text' in sentence:
                        text = sentence.get('text', '')
                        if text.strip():
                            # print(f"Sentence text: {text}")
                            is_end = False
                            if 'sentence_end' in sentence:
                                is_end = sentence.get('sentence_end', False)
                            # 打印调试信息
                            print(f"Recognition result: text='{text}'")

                            # 发出文本识别信号
                            self.recognizer.text_recognized.emit(text, is_end)
                except Exception as e:
                    self.recognizer.error_occurred.emit(f"Error processing recognition result: {e}")

        try:
            # 保存回调对象
            self.callback = Callback(self)

            # 启动识别
            self.recognition = Recognition(
                model='paraformer-realtime-v2',
                format='pcm',
                sample_rate=16000,
                semantic_punctuation_enabled=True,
                callback=self.callback
            )
            self.recognition.start()
            self.is_running = True
            print("Started speech recognition")

        except Exception as e:
            self.error_occurred.emit(f"Error starting recognition: {e}")

    def stop(self) -> None:
        """停止语音识别"""
        if not self.is_running:
            return

        try:
            if self.recognition:
                self.recognition.stop()
            self.is_running = False
        except Exception as e:
            self.error_occurred.emit(f"Error stopping recognition: {e}")

    @Slot(bytes)
    def process_audio_frame(self, audio_data: bytes) -> None:
        """处理音频帧数据"""
        if self.is_running and self.recognition:
            try:
                self.recognition.send_audio_frame(audio_data)
            except Exception as e:
                self.error_occurred.emit(f"Error sending audio frame: {e}")
                # 标记识别为非活跃状态
                self.is_running = False

    def set_api_key(self, api_key: str) -> None:
        """设置 API key"""
        dashscope.api_key = api_key
        self.config.set("api_key", api_key)