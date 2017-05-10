import setuptools


with open('README.md') as fh:
    long_desc = fh.read()


setup_params = dict(
    name='slacky',
    version='0.0.1',
    description='Slack on the command line.',
    long_description=long_desc,
    author="Mathias Bustamante",
    author_email="mathisbc@gmail.com",
    url="",
    packages=['slacky'],
    install_requires=[
        # please keep these lean and mean
        'slackclient>=1.0.0<2.0.0',
    ],
    )


if __name__ == '__main__':
    setuptools.setup(**setup_params)
