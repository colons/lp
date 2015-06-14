from setuptools import setup

with open('README.rst') as readme_file:
    README = readme_file.read()

setup(
    name='lp',
    description='An aid for choosing words in Letterpress',
    url='https://github.com/colons/lp',
    author='colons',
    author_email='pypi@colons.co',
    version='0.1',
    license="BSD",
    platforms=['any'],
    packages=['lp'],
    scripts=['scripts/lp'],
    long_description=README,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
    ],
)
