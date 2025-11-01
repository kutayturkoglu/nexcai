from core.llm_interface import ask_ollama
import sounddevice as sd
import soundfile as sf

def record_audio(filename="input.wav", duration=6, samplerate=16000):
    print("🎙️ Speak now...")
    data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype="int16")
    sd.wait()
    sf.write(filename, data, samplerate)
    print("✅ Recorded:", filename)
    return filename

def conversation_loop():
    while True:
        text = input("You: ")

        if any(word in text.lower() for word in ["exit", "quit", "stop"]):
            print("👋 Goodbye!")
            break

        reply = ask_ollama(f"User said {text}\nReply naturally as NEXAI.")
        print("NEXAI: ", reply)

if __name__ == "__main__":
    print("🧠 NEXA is online. Say something...")
    conversation_loop()