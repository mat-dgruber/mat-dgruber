import os
from make_ascii_svg import image_to_ascii_lines, generate_ascii_svg


def test_make_ascii_svg():
    test_output = "data/test-ascii.svg"

    # Clean up prior test run if exists
    if os.path.exists(test_output):
        os.remove(test_output)

    try:
        lines = image_to_ascii_lines("data/source-prepped.png", width=95)
        assert len(lines) > 0, "ASCII lines list should not be empty"

        res_path = generate_ascii_svg(lines, test_output, svg_width=370)
        assert os.path.exists(res_path), f"Output file {res_path} was not created"

        with open(res_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "<svg" in content, "SVG tag missing from output"
        assert "<clipPath" in content, "clipPath element missing from output"
        assert "<animate" in content, "animate element missing from output"
        assert "font-family" in content, "font-family styling missing from output"
        assert "#38bdf8" in content, "Fill color #38bdf8 missing from output"

        print(f"Test passed: created {res_path} with {len(lines)} ASCII lines")
    finally:
        if os.path.exists(test_output):
            os.remove(test_output)


if __name__ == "__main__":
    test_make_ascii_svg()
