# TESTING IF WHISPER IS FUNCIONING 
import requests
import base64
import numpy as np
import scipy.io.wavfile as wavfile
import io

def create_dummy_audio_b64():
    """Generates a 1-second synthetic beep and encodes it to Base64."""
    samplerate = 16000
    t = np.linspace(0., 1., samplerate)
    data = (32767 * np.sin(2. * np.pi * 440 * t)).astype(np.int16)
    
    buffer = io.BytesIO()
    wavfile.write(buffer, samplerate, data)
    buffer.seek(0)
    
    return base64.b64encode(buffer.read()).decode('utf-8')

def test_tutor_pipeline():
    print("--- 1. TESTING TEXT INPUT PATH ---")
    payload_text = {
        "learner_id": "tester_text_01",
        "text": "Watoto anasoma",
        "audio": None,
        "lang": "sw"
    }
    
    response = requests.post("http://127.0.0.1:8000/session/message", json=payload_text)
    if response.status_code == 200:
        data = response.json()
        print(f"AI Text Reply: {data['reply_text']}")
        if data.get("reply_audio"):
            with open("tutor_response_from_text.wav", "wb") as f:
                f.write(base64.b64decode(data["reply_audio"]))
            print("-> Saved audio to 'tutor_response_from_text.wav'")
    else:
        print("Text test failed:", response.text)

    print("\n--- 2. TESTING AUDIO INPUT PATH ---")
    print("Generating synthetic microphone input...")
    dummy_b64 = create_dummy_audio_b64()
    
    payload_audio = {
        "learner_id": "tester_audio_02",
        "text": None,
        "audio": dummy_b64,
        "lang": "sw"
    }
    
    response = requests.post("http://127.0.0.1:8000/session/message", json=payload_audio)
    if response.status_code == 200:
        data = response.json()
        print(f"AI Text Reply (Whisper Transcription Output): {data['reply_text']}")
        if data.get("reply_audio"):
            with open("tutor_response_from_audio.wav", "wb") as f:
                f.write(base64.b64decode(data["reply_audio"]))
            print("-> Saved audio to 'tutor_response_from_audio.wav'")
    else:
        print("Audio test failed:", response.text)

if __name__ == "__main__":
    test_tutor_pipeline()