import os
import tempfile

from fastapi import UploadFile

from app.services.audio.whisper import transcribe_audio


async def process_audio(file: UploadFile) -> str:
    suffix = os.path.splitext(file.filename)[1]

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    ) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name

    try:
        transcription = transcribe_audio(temp_path)

        return transcription

    finally:
        os.remove(temp_path)