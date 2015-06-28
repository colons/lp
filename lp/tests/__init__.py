import os
from unittest import TestCase

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
