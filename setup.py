from setuptools import setup

with open('README.rst') as readme_file:
    README = readme_file.read()

setup(
    name='lp',
    description='An aid for choosing words in Letterpress',
    url='https://github.com/colons/lp',
    author='colons',
    author_email='pypi@colons.co',
    version='1.0.0',
    license='LICENSE',
    platforms=['any'],
    packages=['lp'],
    scripts=['scripts/lp', 'scripts/lp-solver'],
    long_description=README,
    classifiers=[
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'ansicolors',
        'flask',
        'opencv-python',
        'pillow',
    ],
    tests_require=[
        'nose',
    ],
    test_suite='nose.collector',
    include_package_data=True,
)
