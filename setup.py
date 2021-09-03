from setuptools import setup

setup(
    name='patterns-tests',
    version='0.1',
    install_requires=['pytest'],
    packages=['patterns'],
    package_data={'patterns': ['tests/*', 'tests/**/*']},
)