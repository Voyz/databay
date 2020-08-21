from distutils.core import setup

from setuptools import find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = 'databay',
    packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests", "examples", "docs", "out", "dist"]),
    version = '0.1.4',
    license='Apache-2.0',
    description = 'Databay is a Python interface for scheduled data transfer. It facilitates transfer of (any) data from A to B, on a scheduled interval.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author = 'Voy Zan',
    author_email = 'voy1982@yahoo.co.uk',
    url = 'https://github.com/Voyz/databay',
    download_url = 'https://github.com/Voyz/databay/archive/v0.1.4.tar.gz',
    keywords = ['data transfer', 'data production', 'data consumption', 'schedule', 'scheduled data transfer', 'scheduled transfer', 'data flow', 'repeated data transfer'],
    install_requires=[
        'APScheduler<4.0.0',
        'schedule<1.0.0'
    ],
    extras_require={
        "HttpInlet": ["aiohttp>=3.6.2"],
        "MongoOutlet": ["pymongo>=3.10.1"],
    },
    classifiers=[
        'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3.7',
    ],
)