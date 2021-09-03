from setuptools import setup

setup(
    name='drawbot-tests',
    version='0.1',
    install_requires=['pytest'],
    packages=['src'],
    package_data={'src': ['tests/*', 'tests/**/*']},
)