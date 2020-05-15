import os
from tempfile import mktemp
from unittest import TestCase

from PIL import Image

from lp.game import Grid


IMAGE_DIR = os.path.join(os.path.dirname(__file__), 'images')


class LPTest(TestCase):
    maxDiff = None

    def pngs(self):
        for dirpath, _, filenames in os.walk(IMAGE_DIR):
            dirname = os.path.basename(dirpath)

            for filename in filenames:
                if filename.startswith('.') or not filename.endswith('.png'):
                    continue

                if '_' in filename:
                    meta = filename
                elif '_' in dirname:
                    meta = dirname
                else:
                    raise RuntimeError(
                        'not sure what to do with {}'.format(filename)
                    )
                letters, ownership = os.path.splitext(meta)[0].split('_')
                yield letters, ownership, os.path.join(dirpath, filename)

    def assert_image_matches(self, letters, ownership, name):
        try:
            with open(name, 'rb') as f:
                grid = Grid.from_image(f)
            self.assertEqual(
                [(t.letter, t.ownership) for t in grid.tiles],
                list(zip(letters, ownership))
            )
        except Exception:
            print('failed on {}'.format(name))
            raise

    def test_pngs(self):
        self.assertEqual(len(list(self.pngs())), 20)

    def test_examples_png(self):
        for png in self.pngs():
            self.assert_image_matches(*png)

    def test_examples_jpg(self):
        # iOS transcodes pngs that it uploads to websites, including
        # screenshots, so we need to make sure we can withstand that.

        for letters, ownership, png_path in self.pngs():
            jpg_path = mktemp('.jpg')
            with open(png_path, 'rb') as f:
                image = Image.open(f)
                image = image.convert('RGB')
                image.save(jpg_path, format='JPEG', quality=80)
            self.assert_image_matches(letters, ownership, jpg_path)
