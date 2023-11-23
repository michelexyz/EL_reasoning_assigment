from setuptools import setup

# Read requirements.txt and use its contents for the install_requires argument
with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    install_requires=required
)