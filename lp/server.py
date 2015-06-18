import os
from flask import Flask, request, render_template
from string import lowercase, uppercase, digits
from random import choice

from lp import get_best_words_for_letters
from lp.image import parse_image

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'page.html')


app = Flask(__name__)
app.config.update({
    'MAX_CONTENT_LENGTH': 1024 * 512,
    'SECRET_KEY': ''.join((
        choice(lowercase + uppercase + digits)
        for x in range(128)
    )),
})


def form():
    return {'words': None}


def words():
    image = request.files.get('image')

    if image is None:
        return form()

    parsed = parse_image(image)
    return {
        'words': get_best_words_for_letters(*parsed['letters'])[:50],
        'grid': zip(*parsed['grid']),
        'inf': float('inf'),
    }


@app.route('/', methods=['POST', 'GET'])
def result():
    if request.method == 'GET':
        context = form()
    else:
        context = words()

    return render_template('page.html', **context)


def serve(address):
    if ':' in address:
        host, port = address.split(':', 1)
    else:
        port = address
        host = '127.0.0.1'

    app.run(host=host, port=int(port), debug=True)
    print address


application = app
