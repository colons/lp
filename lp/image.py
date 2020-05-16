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


# the fractions of the edges of tiles we'll cut off to get rid of wiggle
# artifacts
TILE_MARGIN = 6
# the difference in colour that, if seen, makes us think a row isn't homogenous
HOMOGENOUS_ERROR_MARGIN = 5
# the difference we expect to see between game background and unclaimed tile
# backgrounds
COLOUR_DIFF_THRESHOLD = 10


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


def grid_centres(width):
    for i in range(GRID_SIZE):
        yield (
            (i * (width // GRID_SIZE)) +
            ((width // GRID_SIZE) // 2)
        )


def top_of_grid(image):
    """
    find a range of points in the y axis where every point that aligns with the
    centre of a square in a row is within colour_diff() HOMOGENOUS_ERROR_MARGIN
    of each other, and every point search_range below those points has at least
    least colour_diff() COLOUR_DIFF_THRESHOLD. return the y coordinate of the
    row with the different colours, or the point image.width pixels from the
    bottom of the image

    """

    # search_range is the vertical distance of pixels to consider checking
    # against each other. the only real considerations here are 'how far up and
    # down can the horizontal centre of a tile be pushed by tile wiggle', and
    # 'how bad are the jpeg artifacts', both of which shouldn't be changing too
    # much, so:
    wiggle_range = (image.width // GRID_SIZE) // 10
    search_range = max((wiggle_range, 4))

    # begin the search at either 1.5x the image width from the bottom or one
    # grid tile from the top, whichever is the lower point; avoids false
    # positives from status bars or edge artifacts
    start_at = min((
        (image.height - int(1.5 * image.width)),
        (image.width // GRID_SIZE)
    ))

    stop_at = image.height - image.width - search_range + wiggle_range

    if not (stop_at > start_at):
        raise LPImageException(
            "This image doesn't have a narrow enough aspect ratio to be a "
            "Letterpress screenshot as we understand them."
        )

    for ypx in range(start_at, stop_at):
        top_row_colours = set()
        for xpx in grid_centres(image.width):
            top_row_colours.add(image.getpixel((xpx, ypx)))

        # abandon if the row isn't homogenous
        if len(top_row_colours) > 1:
            max_diff = 0
            for colour_a, colour_b in (
                (a, b) for a in top_row_colours for b in top_row_colours
            ):
                diff = colour_diff(colour_a, colour_b)
                if diff > max_diff:
                    max_diff = diff

            if max_diff > HOMOGENOUS_ERROR_MARGIN:
                continue

        # okay, we have a top row that's homogenous, so now we check below:
        bottom_row_colours = set()
        for xpx in grid_centres(image.width):
            bottom_row_colours.add(image.getpixel((xpx, ypx + search_range)))

        if all((
            colour_diff(a, b) > COLOUR_DIFF_THRESHOLD
            for a in top_row_colours for b in bottom_row_colours
        )):
            return ypx + search_range

    raise LPImageException(
        "We couldn't locate the top of the grid in this image."
    )


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
    top_padding = top_of_grid(image)

    crops = []

    for x, y in ((x, y) for y in range(GRID_SIZE) for x in range(GRID_SIZE)):
        coords = (
            (x * base) + base/TILE_MARGIN,
            (y * base) + top_padding + base/TILE_MARGIN,
            ((x + 1) * base) - base/TILE_MARGIN,
            ((y + 1) * base) + top_padding - base/TILE_MARGIN,
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
        crops.append(crop)

        # invert, if necessary
        bg = crop.getpixel((0, 0))
        if bg == 0:
            crop = ImageOps.invert(crop)
        elif bg == 255:
            pass
        else:
            for c in crops:
                c.show()
            raise LPImageException('Could not find clean tiles in the grid.')

        crop = crop.convert('1', dither=NONE)
        crop.save(crop_path)

        letters.append(closest_letter(crop_path))

    shutil.rmtree(dirpath)

    return (''.join(letters), ''.join(ownership))
