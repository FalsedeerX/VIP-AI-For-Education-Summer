from typing import List

import base64
from io import BytesIO
from PIL import Image


def images_to_base64(images: List[Image.Image]) -> List[str]:
    base64_images = []
    for img in images:
        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        buffer.seek(0)

        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        base64_images.append(img_base64)

    return base64_images
