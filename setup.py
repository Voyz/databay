from distutils.core import setup
setup(
    name = 'databay',
    packages = ['databay'],
    version = '0.1.0',
    license='CC0 1.0',
    description = 'Databay is a Python interface for scheduled data transfer. It facilitates transfer of (any) data from A to B, on a scheduled interval.',
    author = 'Voy Zan',
    author_email = 'voy1982@yahoo.co.uk',
    url = 'https://github.com/Voyz/databay',
    download_url = 'https://github.com/Voyz/databay/archive/v0.1.0-alpha.1.tar.gz',
    keywords = ['data transfer', 'data production', 'data consumption', 'schedule', 'scheduled data transfer', 'scheduled transfer', 'data flow', 'repeated data transfer'],
    install_requires=[
        'APScheduler<4.0.0',
        'schedule<1.0.0'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: CREATIVE COMMONS 1 UNIVERSAL',
        'Programming Language :: Python :: 3.7',
    ],
)