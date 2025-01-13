import os
import queue
import logging
import threading
import pyaudio
from vosk import Model, KaldiRecognizer
from config import settings

logger = logging.getLogger(__name__)

class SpeechRecognizer:
    def __init__(self):
        self.model = None
        self.recognizer = None
        self.audio_stream = None
        self.audio_queue = queue.Queue()
        self.running = False
        self.thread = None

    def initialize(self):
        """Initialize the speech recognition system"""
        try:
            # Load Vosk model
            if not os.path.exists(settings.SPEECH_RECOGNITION['MODEL_PATH']):
                raise FileNotFoundError("Vosk model not found")
            
            self.model = Model(settings.SPEECH_RECOGNITION['MODEL_PATH'])
            self.recognizer = KaldiRecognizer(
                self.model, 
                settings.SPEECH_RECOGNITION['SAMPLE_RATE']
            )
            
            # Initialize audio stream
            self.audio = pyaudio.PyAudio()
            self.audio_stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=settings.SPEECH_RECOGNITION['SAMPLE_RATE'],
                input=True,
                frames_per_buffer=settings.SPEECH_RECOGNITION['BUFFER_SIZE'],
                stream_callback=self._audio_callback
            )
            
            logger.info("Speech recognizer initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize speech recognizer: {str(e)}")
            return False

    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Audio stream callback function"""
        self.audio_queue.put(in_data)
        return (None, pyaudio.paContinue)

    def listen(self):
        """Listen for speech and return recognized text"""
        try:
            self.running = True
            final_result = ""
            
            while self.running:
                data = self.audio_queue.get()
                
                if self.recognizer.AcceptWaveform(data):
                    result = self.recognizer.Result()
                    result_dict = eval(result)
                    text = result_dict.get('text', '').strip()
                    
                    if text:
                        final_result = text
                        self.running = False
                        break
            
            return final_result if final_result else None
            
        except Exception as e:
            logger.error(f"Error during speech recognition: {str(e)}")
            return None

    def stop(self):
        """Stop the speech recognition system"""
        self.running = False
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        if self.audio:
            self.audio.terminate()
        logger.info("Speech recognizer stopped")
