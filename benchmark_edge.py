import os
import time
import threading
import psutil
import base64
import io
import numpy as np
import scipy.io.wavfile as wavfile

# Hardware metrics storage
monitoring = False
cpu_logs = []
ram_logs = []

def monitor_resources():
    """Samples CPU and RAM usage every 100ms."""
    global monitoring, cpu_logs, ram_logs
    process = psutil.Process(os.getpid())
    process.cpu_percent(interval=None)  # Prime the CPU counter
    
    while monitoring:
        cpu_logs.append(process.cpu_percent(interval=0.1))
        ram_logs.append(process.memory_info().rss / (1024 * 1024)) # Convert to MB

def start_profiling():
    global monitoring, cpu_logs, ram_logs
    cpu_logs.clear()
    ram_logs.clear()
    monitoring = True
    threading.Thread(target=monitor_resources, daemon=True).start()

def stop_profiling(phase_name, start_time):
    global monitoring
    monitoring = False
    time.sleep(0.2) # Allow final sample
    
    elapsed = time.time() - start_time
    peak_cpu = max(cpu_logs) if cpu_logs else 0
    peak_ram = max(ram_logs) if ram_logs else 0
    avg_ram = sum(ram_logs) / len(ram_logs) if ram_logs else 0
    
    print(f"--- {phase_name.upper()} RESULTS ---")
    print(f"Time Elapsed : {elapsed:.2f} seconds")
    print(f"Peak CPU     : {peak_cpu:.1f}%")
    print(f"Peak RAM     : {peak_ram:.1f} MB (Average: {avg_ram:.1f} MB)\n")

def create_dummy_audio_b64():
    """Generates a 1-second synthetic beep."""
    samplerate = 16000
    t = np.linspace(0., 1., samplerate)
    data = (1000 * np.sin(2. * np.pi * 200 * t)).astype(np.int16)
    buffer = io.BytesIO()
    wavfile.write(buffer, samplerate, data)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')

if __name__ == "__main__":
    print("Initializing edge benchmarking suite...\n")
    
    # Model Loading
    print("PHASE 1: Loading Models into RAM (Whisper + 2x MMS-TTS)...")
    start_time = time.time()
    start_profiling()
    
    # Import inside the script so we capture the exact import memory footprint
    from app.voice_service import VoiceService
    service = VoiceService()
    
    stop_profiling("Model Loading", start_time)
    
    # Generate test payloads
    test_audio = create_dummy_audio_b64()
    test_text = "Vizuri sana! Umepata jibu sahihi kabisa."

    # PHASE 2: STT Inference (Whisper)
    print("PHASE 2: Profiling Speech-to-Text (Swahili Inference)...")
    start_time = time.time()
    start_profiling()
    
    stt_result = service.transcribe_audio(test_audio, "sw")
    
    stop_profiling("Speech-to-Text", start_time)

    # TTS Inference (Meta MMS)
    print("PHASE 3: Profiling Text-to-Speech (Swahili Inference)...")
    start_time = time.time()
    start_profiling()
    
    tts_result = service.synthesize_speech(test_text, "sw")
    
    stop_profiling("Text-to-Speech", start_time)
    
    print("Benchmarking complete.")