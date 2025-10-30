import subprocess
from pathlib import Path

def transcribe(audio_path="input.wav"):
    """
        Convert an audio file to text using whisper.cpp.
        Whisper.cpp has to be compiled and the model file must be downloaded beforehand.
    """

    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    whisper_exec = Path(__file__).resolve().parents[1] / "whisper.cpp" / "build" / "bin" / "whisper-cli"
    model_path   = Path(__file__).resolve().parents[1] / "whisper.cpp" / "models" / "ggml-base.en.bin"
    if not whisper_exec.exists():
        raise FileNotFoundError(f"Whisper executable not found: {whisper_exec}")
    
    model_path = Path(model_path)
    if not model_path.exists():
        raise FileNotFoundError(f"Model path not found: {model_path}")
    
    cmd = [
        str(whisper_exec),
        "-m", str(model_path),
        "-f", str(audio_path),
        "-l", "en", # English
        "-otxt"
    ]

    print("Running whisper for the speech recognition...")
    subprocess.run(cmd, check=True)
    print("Whisper finished")

    txt_output = audio_path.with_suffix(".wav.txt")
    if not txt_output.exists():
        raise RuntimeError(f"Output text not found: {txt_output}")
    
    return txt_output.read_text().strip()
