import sys
from pathlib import Path
import os 

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
from nexcai_core.speech_to_text import transcribe
if __name__ == "__main__":
    path = os.path.join(ROOT,"data/test_input_1.wav")
    text = transcribe(path)
    print("Transcribed text: ", text)