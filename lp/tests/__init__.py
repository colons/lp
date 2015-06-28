import os
from tempfile import mktemp
from unittest import TestCase

from PIL import Image

from lp.game import Grid


IMAGE_DIR = os.path.join(os.path.dirname(__file__), 'images')


class LPTest(TestCase):
    def pngs(self):
        for filename in os.listdir(IMAGE_DIR):
            if filename.startswith('.') or not filename.endswith('.png'):
                continue

            letters, ownership = os.path.splitext(filename)[0].split('_')
            yield letters, ownership, os.path.join(IMAGE_DIR, filename)

    def assert_image_matches(self, letters, ownership, name):
        grid = Grid.from_image(open(name))
        self.assertEqual(
            [(t.letter, t.ownership) for t in grid.tiles],
            zip(letters, ownership)
        )

    def test_examples_png(self):
        for png in self.pngs():
            self.assert_image_matches(*png)

    def test_examples_jpg(self):
        # iOS transcodes pngs that it uploads to websites, including
        # screenshots, so we need to make sure we can withstand that.

        for letters, ownership, png_path in self.pngs():
            jpg_path = mktemp('.jpg')
            Image.open(png_path).save(jpg_path, format='JPEG', quality=80)
            self.assert_image_matches(letters, ownership, jpg_path)
