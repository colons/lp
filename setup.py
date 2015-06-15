from setuptools import setup
from os import listdir, path

with open('README.rst') as readme_file:
    README = readme_file.read()

WORDLIST_DIR = path.join('lp', 'words', 'Words')

setup(
    name='lp',
    description='An aid for choosing words in Letterpress',
    url='https://github.com/colons/lp',
    author='colons',
    author_email='pypi@colons.co',
    version='0.2.2',
    license='LICENSE',
    platforms=['any'],
    packages=['lp'],
    scripts=['scripts/lp'],
    long_description=README,
    classifiers=[
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'ansicolors',
    ],
    data_files=[(WORDLIST_DIR, [
        path.join(WORDLIST_DIR, l) for l in
        listdir(WORDLIST_DIR)
    ])],
)
