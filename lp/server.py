import os
from flask import Flask, request, render_template, session, abort

from lp.game import Grid
from lp.image import LPImageException

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'page.html')


app = Flask(__name__)
app.config.update({
    'MAX_CONTENT_LENGTH': 1024 * 1024 * 4,
    'SECRET_KEY': os.environ.get('SECRET_KEY', os.urandom(128))
})


@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403)


def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = repr(os.urandom(128))
    return session['_csrf_token']


app.jinja_env.globals['csrf_token'] = generate_csrf_token


def words():
    image = request.files.get('image')
    priority = request.form.get('priority')

    if priority not in Grid.PRIORITIES.keys():
        priority = Grid.NET_SCORE_PRIORITY

    if not image:
        return {}

    try:
        grid = Grid.from_image(image, priority=priority)
    except LPImageException as e:
        return {'error': str(e)}

    return {
        'grid': grid,
        'inf': float('inf'),
    }


@app.route('/', methods=['POST', 'GET'])
def result():
    context = {
        'grid': None,
        'priorities': Grid.PRIORITIES,
    }

    if request.method == 'POST':
        context.update(words())

    return render_template('page.html', **context)


def serve(address):
    if ':' in address:
        host, port = address.split(':', 1)
    else:
        port = address
        host = '127.0.0.1'

    app.run(host=host, port=int(port), debug=True)
    print(address)


application = app
