lp
==

A script and WSGI app for cheating at Letterpress. Can derive the state of a
game and make recommendations based on screenshots uploaded to a web app.

Requires Python 3.6 or later.

::

   $ [sudo] pip install lp
   $ lp IMG_0001.PNG
   win - scruzes
   win - schmalzes
   win - schmaltzes
    12 - chamfers
    11 - screams
    11 - marquess
    11 - masquers
    11 - scammers
    11 - scampers
    11 - scamster
   $ lp --listen=127.0.0.1:8081

You can also invoke lp with ``lp-solver`` if you're worried about accidentally
printing things.

Run ``lp --help`` (or ``lp-solver --help``) for more information on command
line invocation. If you want to host the web version, ``lp/server.py`` is the
WSGI app you should point your server at.
