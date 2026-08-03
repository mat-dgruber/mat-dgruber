import os
from make_info_card import generate_info_card_svg


def test_make_info_card():
    test_output = "data/test-info-card.svg"

    # Clean up prior test run if exists
    if os.path.exists(test_output):
        os.remove(test_output)

    try:
        res_path = generate_info_card_svg(test_output)
        assert os.path.exists(res_path), f"Output file {res_path} was not created"

        with open(res_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "<svg" in content, "SVG tag missing from output"
        assert "matheus@cpb ~ neofetch" in content, "Header title missing from output"
        assert "Engenheiro de Software Pleno" in content, "Role text missing from output"
        assert "#0d1117" in content, "Background color #0d1117 missing from output"
        assert "#30363d" in content, "Border color #30363d missing from output"

        print(f"Test passed: created {res_path}")
    finally:
        if os.path.exists(test_output):
            os.remove(test_output)


if __name__ == "__main__":
    test_make_info_card()
