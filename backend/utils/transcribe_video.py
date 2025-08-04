import whisper

def transcribe_video(file_path: str) -> str:
    model = whisper.load_model("base")
    result = model.transcribe(file_path)
    return result["text"]