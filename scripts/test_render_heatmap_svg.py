import os
import sys
import unittest

from render_heatmap_svg import render_heatmap_svg


class TestRenderHeatmapSVG(unittest.TestCase):
    def test_render_heatmap_svg(self):
        json_path = "data/contributions.json"
        output_svg = "contrib-heatmap.svg"

        if os.path.exists(output_svg):
            os.remove(output_svg)

        res_path = render_heatmap_svg(json_path, output_svg)

        # Assert output path
        self.assertEqual(res_path, output_svg)
        self.assertTrue(os.path.exists(output_svg), "SVG file was not created.")

        with open(output_svg, "r", encoding="utf-8") as f:
            content = f.read()

        # Assert SVG root element
        self.assertIn("<svg", content, "SVG tag not found in output.")
        # Assert Header Title
        self.assertIn(
            "matheus@github ~ ./contributions.sh --year 2025-2026",
            content,
            "Header title not found in output.",
        )
        # Assert day-box presence
        self.assertIn("day-box", content, "day-box elements not found in output.")


if __name__ == "__main__":
    unittest.main()
