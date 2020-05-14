import os
import shutil
try:
    from string import ascii_uppercase as uppercase
except ImportError:
    from string import uppercase
import tempfile

import cv2
import numpy
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
from PIL.Image import NONE

from lp.game import GRID_SIZE, NOBODY, OPPONENT, PLAYER


class LPImageException(Exception):
    pass


# as RGB tuples of opponent defended, opponent, unclaimed, ours, defended ours.
# we actually use the background colour for unclaimed to make shortlisting our
# themes easier, as there are actually two unclaimed colours in each theme
# (look closely :3)

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


def invariant_for(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, threshold = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)
    mask = threshold > 0
    cropped = threshold[numpy.ix_(mask.any(1), mask.any(0))]
    if not all(cropped.shape):
        raise LPImageException(
            "We couldn't see a whole grid in this image; it might be "
            "landscape or just very consistently coloured on the left side."
        )
    resized = cv2.resize(
        cropped, (30, 30),
        interpolation=cv2.INTER_NEAREST,
    )
    # print('\n'.join((
    #     ''.join(( '0' if px else '-' for px in r))
    # ) for r in resized))
    return resized


LETTER_INVARIANTS = {
    letter: invariant_for(os.path.join(
        os.path.dirname(__file__), 'images', '{}.png'.format(letter)
    )) for letter in uppercase
}


def colour_diff(a, b):
    return sum(
        abs(ac - bc)
        for ac, bc in zip(a, b)
    )


def closest_colour(colour, colours):
    return min(colours, key=lambda c: colour_diff(c, colour))


def compare_invariants(a, b):
    diff = 0

    for row_a, row_b in zip(a, b):
        for px_a, px_b in zip(row_a, row_b):
            if px_a != px_b:
                diff += 1

    return diff


def closest_letter(image_path):
    invariant = invariant_for(image_path)

    return min(
        LETTER_INVARIANTS.keys(),
        key=lambda l: compare_invariants(LETTER_INVARIANTS[l], invariant),
    )


def distance_to_different_colour_from_bottom(image):
    top_left = image.getpixel((0, 0))
    for i in range(1, image.height):
        px = image.getpixel((0, image.height-i))
        if colour_diff(top_left, px) > 10:
            return i-1
    raise LPImageException('Could not find the bottom of the grid')


def parse_image(image):
    letters = []
    ownership = []

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
        c: (OPPONENT, OPPONENT, NOBODY, PLAYER, PLAYER)[i]
        for theme in (
            t for t in THEMES
            if t[2] == unclaimed_colour
        )
        for i, c in enumerate(theme)
    }

    width, height = image.size
    base = width / GRID_SIZE
    bottom_padding = distance_to_different_colour_from_bottom(image)
    top_padding = (height - width) - bottom_padding

    for x, y in ((x, y) for y in range(GRID_SIZE) for x in range(GRID_SIZE)):
        coords = (
            (x * base) + base/6,
            (y * base) + top_padding + base/6,
            ((x + 1) * base) - base/6,
            ((y + 1) * base) + top_padding - base/6,
        )
        crop = image.crop(coords)
        crop_path = os.path.join(dirpath, '{}_{}.png'.format(x, y))

        ownership.append(
            colours[closest_colour(crop.getpixel((0, 0)), colours.keys())]
        )

        crop = crop.convert('L')
        crop = ImageOps.autocontrast(crop, 0)

        # remove weird jpg artifacts:
        gaussian = ImageFilter.GaussianBlur(radius=base/100)
        crop = crop.filter(gaussian)
        contraster = ImageEnhance.Contrast(crop)
        crop = contraster.enhance(10)

        # invert, if necessary
        bg = crop.getpixel((0, 0))
        if bg == 0:
            crop = ImageOps.invert(crop)
        elif bg == 255:
            pass
        else:
            raise LPImageException('Could not find clean tiles in the grid.')

        crop = crop.convert('1', dither=NONE)
        crop.save(crop_path)

        letters.append(closest_letter(crop_path))

    shutil.rmtree(dirpath)

    return (''.join(letters), ''.join(ownership))
