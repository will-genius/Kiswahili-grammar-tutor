import base64
import logging
import tempfile
import os
from faster_whisper import WhisperModel
import logging
import scipy.io.wavfile
import torch 
from transformers import VitsModel, AutoTokenizer

logger = logging.getLogger(__name__)

class VoiceService:
    def __init__(self):
        # STT Model
        logger.info("Loading local Whisper model into memory...")
       
        self.stt_model = WhisperModel(
            "tiny", 
            device="cpu", 
            compute_type="int8", 
            cpu_threads=4
        )
        #  Load Swahili MMS-TTS Model and Tokenizer
        logger.info("Loading local Swahili MMS-TTS model...")
        self.tts_tokenizer_sw = AutoTokenizer.from_pretrained("facebook/mms-tts-swh")
        self.tts_model_sw = VitsModel.from_pretrained("facebook/mms-tts-swh")
        
        #  Load English MMS-TTS Model and Tokenizer
        logger.info("Loading local English MMS-TTS model...")
        self.tts_tokenizer_en = AutoTokenizer.from_pretrained("facebook/mms-tts-eng")
        self.tts_model_en = VitsModel.from_pretrained("facebook/mms-tts-eng")

    def transcribe_audio(self, audio_b64: str, lang_toggle: str) -> str:
        logger.info(f"Decoding base64 audio payload for local {lang_toggle} transcription...")
        import numpy as np
        import scipy.io.wavfile as wavfile
        
        audio_bytes = base64.b64decode(audio_b64)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_bytes)
            temp_file_path = temp_audio.name

        try:
            # Read the audio manually using SciPy to bypass the broken PyAV library
            sample_rate, audio_data = wavfile.read(temp_file_path)
            
            # Whisper expects a mono channel. If it's stereo, grab the first channel.
            if len(audio_data.shape) > 1:
                audio_data = audio_data[:, 0]
                
            # Whisper expects audio as a float32 array normalized between -1.0 and 1.0
            audio_array = audio_data.astype(np.float32) / 32768.0
            
            # Pass the raw array directly into the model
            whisper_lang = "sw" if lang_toggle == "sw" else "en"
            
            # Enable VAD filter to ignore silence and beeps instantly
            segments, info = self.stt_model.transcribe(
                audio_array, 
                language=whisper_lang,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            transcription = "".join([segment.text for segment in segments])
            return transcription.strip()
            
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    def synthesize_speech(self, text: str, lang_toggle: str) -> str:
        """
        Runs local MMS-TTS offline, saves to a temp WAV, and encodes to base64.
        """
        logger.info(f"Synthesizing {lang_toggle} speech for: {text}")
        
        # Route text to the correct tokenizer and model
        if lang_toggle == "sw":
            inputs = self.tts_tokenizer_sw(text, return_tensors="pt")
            with torch.no_grad():
                output = self.tts_model_sw(**inputs).waveform
        else:
            inputs = self.tts_tokenizer_en(text, return_tensors="pt")
            with torch.no_grad():
                output = self.tts_model_en(**inputs).waveform

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_file_path = temp_audio.name

        try:
            # Convert the generated PyTorch audio tensor to a WAV file
            audio_data = output.squeeze().cpu().numpy()
            scipy.io.wavfile.write(temp_file_path, rate=16000, data=audio_data)
            
            with open(temp_file_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
                
            return base64.b64encode(audio_bytes).decode('utf-8')
            
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)