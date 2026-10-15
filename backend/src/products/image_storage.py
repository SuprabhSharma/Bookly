import io
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

from src.config import BASE_DIR

PRODUCT_IMAGE_DIR = BASE_DIR / "uploads" / "products"
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_PRODUCT_IMAGES = 10
MAX_IMAGE_DIMENSION = 1600


async def save_product_images(files: list[UploadFile]) -> list[str]:
    if len(files) > MAX_PRODUCT_IMAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You can upload at most {MAX_PRODUCT_IMAGES} images.",
        )

    PRODUCT_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    urls: list[str] = []
    try:
        for file in files:
            if not file.content_type or not file.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{file.filename or 'File'} is not a supported image.",
                )

            contents = await file.read(MAX_UPLOAD_BYTES + 1)
            if len(contents) > MAX_UPLOAD_BYTES:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Each image must be 10 MB or smaller.",
                )

            try:
                with Image.open(io.BytesIO(contents)) as source:
                    image = source.convert("RGB")
                    image.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), Image.Resampling.LANCZOS)
                    image_uid = uuid.uuid4().hex
                    output_path = PRODUCT_IMAGE_DIR / f"{image_uid}.webp"
                    image.save(output_path, "WEBP", quality=82, method=6, optimize=True)
            except (UnidentifiedImageError, OSError) as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{file.filename or 'File'} is not a valid image.",
                ) from exc

            urls.append(f"/media/products/{output_path.name}")
    except Exception:
        for url in urls:
            delete_product_image(url)
        raise
    finally:
        await file.close()

    return urls


def delete_product_image(url: str) -> None:
    prefix = "/media/products/"
    if not url.startswith(prefix):
        return
    path = PRODUCT_IMAGE_DIR / Path(url.removeprefix(prefix)).name
    if path.parent == PRODUCT_IMAGE_DIR and path.exists():
        path.unlink()
