import os
from flask import Flask, request, render_template, session, abort
from string import lowercase, uppercase, digits
from random import choice

from lp import get_best_words_for_letters
from lp.image import parse_image

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'page.html')


def random_string():
    return ''.join((
        choice(lowercase + uppercase + digits)
        for x in range(128)
    ))


app = Flask(__name__)
app.config.update({
    'MAX_CONTENT_LENGTH': 1024 * 512,
    'SECRET_KEY': random_string(),
})


@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403)


def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = random_string()
    return session['_csrf_token']


app.jinja_env.globals['csrf_token'] = generate_csrf_token


def form():
    return {'words': None}


def words():
    image = request.files.get('image')

    if not image:
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
