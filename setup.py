#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='django-partial-index',
    packages=['partial_index'],  # this must be the same as the name above
    version='0.1',
    description='PostgreSQL partial indexes for Django',
    author='Mattias Linnap',
    author_email='mattias@linnap.com',
    url='https://github.com/mattiaslinnap/django-partial-index',
    download_url='https://github.com/mattiaslinnap/django-partial-index/archive/0.1.tar.gz',  # I'll explain this in a second
    license='BSD',
    install_requires=[],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Database',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
