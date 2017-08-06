#!/usr/bin/env python

from setuptools import setup


setup(
    name='django-partial-index',
    packages=['partial_index'],
    version='0.2.0',
    description='PostgreSQL partial indexes for Django',
    long_description=open('README.md').read(),
    author='Mattias Linnap',
    author_email='mattias@linnap.com',
    url='https://github.com/mattiaslinnap/django-partial-index',
    download_url='https://github.com/mattiaslinnap/django-partial-index/archive/0.2.0.tar.gz',
    license='BSD',
    install_requires=[],
    classifiers=[
        'Development Status :: 4 - Beta',
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
