lp
==

A script and WSGI app for cheating at Letterpress. Can derive the state of a
game and make recommendations based on screenshots uploaded to a web app.
Letter recognition requires tesseract, which you can probably get from apt or
homebrew or whatever your favourite package manager is.

::

   $ brew install tesseract || sudo apt-get install tesseract-ocr tesseract-ocr-eng || yum or uhh yaourt or something
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

Run ``lp --help`` for more information on command line invocation. If you want
to host the web version, ``lp/server.py`` is the WSGI app you should point your
server at.
