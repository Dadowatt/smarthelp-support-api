import os
import shutil
import uuid

from fastapi import UploadFile

from app.services.vision.clip import analyze_image


UPLOAD_DIR = "uploads"


async def process_image(image: UploadFile):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    extension = os.path.splitext(image.filename)[1]

    filename = f"{uuid.uuid4()}{extension}"

    image_path = os.path.join(UPLOAD_DIR, filename)

    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    try:
        result = analyze_image(image_path)
        return result

    finally:
        if os.path.exists(image_path):
            os.remove(image_path)