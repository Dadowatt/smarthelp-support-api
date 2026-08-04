from fastapi import HTTPException, UploadFile

ALLOWED_AUDIO_TYPES = {
    "audio/mpeg",
    "audio/wav",
    "audio/x-wav",
}

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/jpg",
    "image/webp",
}


def validate_audio_file(file: UploadFile) -> None:
    if file.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Format audio non supporté."
        )


def validate_image_file(file: UploadFile) -> None:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Format image non supporté."
        )


MAX_IMAGE_SIZE = 5 * 1024 * 1024   # 5 MB
MAX_AUDIO_SIZE = 15 * 1024 * 1024   # 15 MB

async def validate_audio_size(file: UploadFile) -> None:
    content = await file.read()

    if len(content) > MAX_AUDIO_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Fichier audio trop volumineux."
        )

    await file.seek(0)

async def validate_image_size(file: UploadFile) -> None:
    content = await file.read()

    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Image trop volumineuse."
        )

    await file.seek(0)