from setuptools import setup, find_packages


setup(
    name="google_input",
    version="0.1",
    author='tomoemon',
    packages={'google_input': 'google_input'},
    package_data={'google_input': ['data/*.txt']}
)
