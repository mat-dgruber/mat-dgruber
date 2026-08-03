import os
import sys
import cv2
import numpy as np
from PIL import Image
from rembg import remove


def prep_photo(input_path: str, output_path: str) -> None:
    """Removes background from input image, applies CLAHE grayscale,

    composites over a white background, and saves to output_path.
    """
    img = Image.open(input_path)
    img_nobg = remove(img)
    img_np = np.array(img_nobg)

    rgb = img_np[:, :, :3]
    alpha = img_np[:, :, 3] / 255.0

    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray_clahe = clahe.apply(gray)

    composite = (gray_clahe.astype(np.float32) * alpha + 255.0 * (1.0 - alpha)).astype(np.uint8)

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    result_img = Image.fromarray(composite)
    result_img.save(output_path)


if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "assets/IMG_2250.jpg"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "data/source-prepped.png"
    prep_photo(input_file, output_file)
