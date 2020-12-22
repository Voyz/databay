from distutils.core import setup

from setuptools import find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='databay',
    packages=find_packages(exclude=[
        "*.tests", "*.tests.*", "tests.*", "tests", "examples", "docs", "out", "dist"]),
    version='0.2.0',
    license='Apache-2.0',
    description='Databay is a Python interface for scheduled data transfer. It facilitates transfer of (any) data from A to B, on a scheduled interval.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Voy Zan, Charles Pierse',
    author_email='voy1982@yahoo.co.uk',
    url='https://github.com/Voyz/databay',
    keywords=['data transfer', 'data production', 'data consumption', 'schedule',
                'scheduled data transfer', 'scheduled transfer', 'data flow', 'repeated data transfer'],
    install_requires=[
        'APScheduler<4.0.0',
        'schedule<1.0.0'
    ],
    extras_require={
        "HttpInlet": ["aiohttp>=3.6.2"],
        "MongoOutlet": ["pymongo>=3.10.1"],
        "all": ["aiohttp>=3.6.2", "pymongo>=3.10.1"]
    },
    classifiers=[
        'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]
)