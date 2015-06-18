lp
==

A script and WSGI app for cheating at Letterpress. Can derive the state of a
game and make recommendations based on screenshots uploaded to a web app.
Letter recognition requires tesseract, which you can probably get from apt or
homebrew or whatever your favourite package manager is.

::

   $ pip install lp  # you might need sudo to install things with pip
   $ lp ummpuatlt cmsfreq zs krlbudh
   The current score is 7-16. There are 2 tiles left.
   win - schmaltzes
   win - schmalzes
   win - scruzes
    12 - chamfers
    11 - bumsuckers
    11 - charmless
    11 - clubmasters
    11 - craftless
    11 - feldschars
    11 - lumpsuckers
   $ lp --listen=127.0.0.1:8081

Run ``lp --help`` for more information.
