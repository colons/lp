import os
from tempfile import mkdtemp
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

    def test_examples_png(self):
        for letters, ownership, name in self.pngs():
            grid = Grid.from_image(open(name))
            self.assertEqual(
                [(t.letter, t.ownership) for t in grid.tiles],
                zip(letters, ownership)
            )

    def test_examples_jpg(self):
        # iOS transcodes pngs that it uploads to websites, including
        # screenshots, so we need to make sure we can withstand that.

        jpg_dir = mkdtemp()
        for letters, ownership, png_path in self.pngs():
            jpg_path = os.path.join(
                jpg_dir, '{}_{}.jpg'.format(letters, ownership)
            )
            Image.open(png_path).save(jpg_path, format='JPEG', quality=80)
            grid = Grid.from_image(open(jpg_path))
            self.assertEqual(
                zip(letters, ownership),
                [(t.letter, t.ownership) for t in grid.tiles],
            )
