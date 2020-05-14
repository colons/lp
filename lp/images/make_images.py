"""
Create a bunch of images to compare tiles we're looking at against. This should
really only need to be run once, ever, and the results will be bundled with lp.
"""

import os

from PIL import Image, ImageDraw, ImageFont


SIZE = 1000


def make_image_for(letter):
    image = Image.new('1', (SIZE, SIZE), color='white')
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(os.path.join(
        os.path.dirname(__file__), 'MuseoSansRounded700.otf',
    ), int(SIZE * 0.95))
    w, h = font.getsize(letter)
    h = int(h * 1.3)  # the alignment gets a bit off, idk
    draw.text(
        ((SIZE-w)//2, (SIZE-h)//2),
        letter, align='center', font=font, fill='black'
    )

    image.save('{}.png'.format(letter))


if __name__ == '__main__':
    from string import ascii_uppercase
    for letter in ascii_uppercase:
        make_image_for(letter)
