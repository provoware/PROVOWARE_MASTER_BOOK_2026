"""Echte Chromium-Prüfung: Offline-Ansichten, kleine Fenster und große Schrift.

Ausführen: python -m playwright install chromium && python tests/test_responsive_browser.py
Keine kanonischen Daten werden geschrieben.
"""
from pathlib import Path
import unittest

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class ResponsiveBrowserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def open_page(self, name, width, height, large_text=False):
        page = self.browser.new_page(viewport={"width": width, "height": height})
        page.goto((ROOT / name).as_uri(), wait_until="load")
        if large_text:
            page.evaluate("document.documentElement.style.fontSize = '200%'")
        return page

    def assert_no_horizontal_scroll(self, page, label):
        dims = page.evaluate("""() => ({
            viewport: document.documentElement.clientWidth,
            body: document.body.scrollWidth,
            root: document.documentElement.scrollWidth
        })""")
        self.assertLessEqual(
            max(dims["body"], dims["root"]), dims["viewport"] + 1,
            f"{label}: unerlaubtes horizontales Scrollen: {dims}"
        )

    def test_offline_views_at_800_and_narrow_widths(self):
        for name in ("index.html", "preview.html"):
            for width, height in ((1280, 720), (800, 600), (400, 300), (320, 568)):
                with self.subTest(page=name, viewport=width):
                    page = self.open_page(name, width, height)
                    try:
                        self.assert_no_horizontal_scroll(page, f"{name} {width}x{height}")
                        if width <= 800:
                            cols = page.locator("main").evaluate(
                                "(el) => getComputedStyle(el).gridTemplateColumns"
                            )
                            self.assertEqual(len(cols.split()), 1, f"{name}: {cols}")
                    finally:
                        page.close()

    def test_800x600_with_double_font_size(self):
        for name in ("index.html", "preview.html"):
            with self.subTest(page=name):
                page = self.open_page(name, 800, 600, large_text=True)
                try:
                    self.assert_no_horizontal_scroll(page, f"{name} 800x600 200% Schrift")
                    self.assertTrue(page.locator("main").is_visible())
                finally:
                    page.close()

    def test_keyboard_cards_and_preview_selection(self):
        page = self.open_page("index.html", 800, 600)
        try:
            card = page.locator("#cards .card").first
            self.assertGreater(page.locator("#cards .card").count(), 0)
            card.focus()
            card.press("Enter")
            self.assertNotEqual(page.locator("#detail h2").inner_text(), "Eintrag wählen")
            self.assert_no_horizontal_scroll(page, "index nach Tastaturauswahl")
        finally:
            page.close()

        page = self.open_page("preview.html", 800, 600)
        try:
            candidate = page.locator("#candidate-list button").first
            self.assertGreater(page.locator("#candidate-list button").count(), 0)
            candidate.focus()
            candidate.press("Enter")
            self.assertNotIn("Kandidaten wählen.", page.locator("#plan").inner_text())
            self.assert_no_horizontal_scroll(page, "preview nach Tastaturauswahl")
        finally:
            page.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
