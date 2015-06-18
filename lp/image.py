from __future__ import unicode_literals, print_function

import os
import shutil
from string import uppercase
import subprocess
import tempfile

from PIL import Image, ImageOps

from lp import GRID_SIZE


# as RGB tuples of enemy defended, enemy, unclaimed, ours, defended ours (or
# EeumM, as we refer to it internally). we actually use the background colour
# for unclaimed to make shortlisting our themes easier.
THEMES = (
    # light
    ((249, 42, 36), (242, 132, 123), (236, 235, 231), (103, 187, 242),
     (23, 142, 254)),
    # pop
    ((249, 0, 186), (132, 0, 103), (37, 37, 37), (71, 138, 19),
     (113, 255, 10)),
    # retro
    ((229, 74, 54), (239, 148, 114), (249, 232, 185), (181, 111, 218),
     (119, 0, 255)),
    # dark
    ((249, 42, 36), (132, 41, 37), (37, 37, 37), (23, 97, 134),
     (28, 170, 255)),
    # forest
    ((20, 82, 45), (104, 149, 119), (217, 225, 206), (234, 181, 89),
     (251, 138, 9)),
    # glow
    ((226, 0, 86), (120, 7, 60), (37, 37, 37), (60, 137, 100), (86, 255, 176)),
    # pink
    ((68, 42, 36), (154, 120, 123), (253, 215, 232), (250, 80, 227),
     (249, 0, 221)),
    # contrast
    ((0, 0, 0), (108, 108, 108), (255, 255, 255), (129, 255, 109),
     (45, 255, 9)),
)


def colour_diff(a, b):
    return sum(
        abs(ac - bc)
        for ac, bc in zip(a, b)
    )


def closest_colour(colour, colours):
    return min(colours, key=lambda c: colour_diff(c, colour))


def parse_image(image):
    letters, defended, targets, unclaimed, owned, states = (
        [], [], [], [], [], [],
    )

    dirpath = tempfile.mkdtemp()
    image = Image.open(image).convert('RGB')

    # we can look at the top left pixel of the image to find out what our
    # unclaimed colour is, and thereby produce a shortlist of the themes that
    # this could be a screenshot of
    #
    # it must be noted that this is not a perfect approach; the pink theme, for
    # example, has slightly different colours for unclaimed and the background
    unclaimed_colours = [c[2] for c in THEMES]
    unclaimed_colour = closest_colour(image.getpixel((3, 3)),
                                      unclaimed_colours)
    colours = {
        c: 'EeumM'[i]
        for theme in (
            t for t in THEMES
            if t[2] == unclaimed_colour
        )
        for i, c in enumerate(theme)
    }

    tess_config_file = tempfile.NamedTemporaryFile(mode='w+')
    tess_config_file.write('tessedit_char_whitelist {}\n'.format(uppercase))

    width, height = image.size
    base = width/GRID_SIZE
    top_padding = height-width

    for x, y in ((x, y) for y in range(GRID_SIZE) for x in range(GRID_SIZE)):
        coords = (
            (x * base) + base/6,
            (y * base) + top_padding + base/6,
            ((x + 1) * base) - base/6,
            ((y + 1) * base) + top_padding - base/6,
        )
        crop = image.crop(coords)
        crop_path = os.path.join(dirpath, '{}_{}.png'.format(x, y))
        ImageOps.posterize(crop, 2).save(crop_path)

        state = colours[closest_colour(crop.getpixel((0, 0)), colours.keys())]
        states.append(state)

        subprocess.check_output(
            ['tesseract', crop_path, os.path.join(dirpath, 'letter'), '-psm',
             '10', tess_config_file.name],
            stderr=subprocess.STDOUT,
        )

        with open(os.path.join(dirpath, 'letter.txt')) as lfile:
            # tesseract doesn't parse | as I, so we assume if it's blank:
            letter = lfile.read().strip() or 'I'

        letters.append(letter)

        {'E': defended, 'e': targets, 'u': unclaimed, 'm': owned, 'M': owned,
         }[state].append(letter)

    shutil.rmtree(dirpath)

    return {
        'grid': (states, letters),
        'letters': tuple((
            ''.join(l).lower() for l in (defended, targets, unclaimed, owned)
        ))
    }
