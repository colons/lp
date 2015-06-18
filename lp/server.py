import os
from bottle import default_app, get, post, request, run, view

from lp import get_best_words_for_letters
from lp.image import parse_image

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'page.html')


@post('/')
@view(TEMPLATE_PATH)
def result():
    parsed = parse_image(request.files.get('image').file)
    return {
        'words': get_best_words_for_letters(*parsed['letters']),
        'grid': parsed['grid'],
    }


@get('/')
@view(TEMPLATE_PATH)
def form():
    return {'words': None}


application = default_app()


def serve(address):
    if ':' in address:
        host, port = address.split(':', 1)
    else:
        port = address
        host = '127.0.0.1'

    run(app=application, host=host, port=int(port))
    print address
