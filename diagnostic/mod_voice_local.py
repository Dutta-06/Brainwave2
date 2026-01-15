import speech_recognition as sr
import pyttsx3
import whisper
import warnings
import os

# Suppress warnings
warnings.filterwarnings("ignore")

class VoiceBot:
    def __init__(self):
        print("[System] Loading local Whisper model (tiny) on PyTorch...")
        # 'tiny' is ~75MB. It runs on CPU.
        self.stt_model = whisper.load_model("tiny")
        
        # Initialize Text-to-Speech (Offline)
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150) 

    def speak(self, text):
        print(f"[Bot]: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def listen(self, duration=5):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        print("[System] Listening...")
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            audio_data = recognizer.record(source, duration=duration)
            
            with open("temp_audio.wav", "wb") as f:
                f.write(audio_data.get_wav_data())

        print("[System] Transcribing...")
        # Whisper uses PyTorch internally
        result = self.stt_model.transcribe("temp_audio.wav")
        text = result['text'].strip()
        
        if os.path.exists("temp_audio.wav"):
            os.remove("temp_audio.wav")
            
        return text

if __name__ == "__main__":
    bot = VoiceBot()
    # bot.speak("System Online.")
    # print(bot.listen())