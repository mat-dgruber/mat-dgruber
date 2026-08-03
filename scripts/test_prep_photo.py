import os
from PIL import Image
from prep_photo import prep_photo


def test_prep_photo():
    test_output = "data/test-prepped.png"

    # Clean up prior test run if exists
    if os.path.exists(test_output):
        os.remove(test_output)

    try:
        prep_photo("assets/IMG_2250.jpg", test_output)

        assert os.path.exists(test_output), f"Output file {test_output} was not created"

        with Image.open(test_output) as img:
            width, height = img.size
            assert width > 0 and height > 0, f"Invalid dimensions: {width}x{height}"

        print(f"Test passed: created {test_output} ({width}x{height})")
    finally:
        if os.path.exists(test_output):
            os.remove(test_output)


if __name__ == "__main__":
    test_prep_photo()
