import whisper
import wave
import speech_recognition as sr
import pyaudio

p = pyaudio.PyAudio()
FORMAT = pyaudio.paInt16
RATE = 96000
model = whisper.load_model('medium.en')

def save_audio(audio_data, filename):
    # Write combined data to WAV file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(audio_data))
    #convert_audio_data_to_text(filename)

def convert_audio_data_to_text(file, sample_rate=RATE):
    # Initialize the recognizer
    result = model.transcribe(file, fp16=False)
    print(result['text']) 
    """ recognizer = sr.Recognizer()
    
    # Convert PCM data to bytes
    audio_data_bytes = pcm_data
    
    # Create an AudioData instance
    audio_data = sr.AudioData(audio_data_bytes, sample_rate, 2)  # Assuming 16-bit samples (2 bytes per sample)
    
    try:
        # Use Google Web Speech API to recognize the text
        text = recognizer.recognize_whisper(audio_data)
        print(f"Recognized text: {text}")
        return text
    except sr.UnknownValueError:
        print("Google Web Speech API could not understand the audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Web Speech API; {e}") """
