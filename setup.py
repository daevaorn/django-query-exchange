#!/usr/bin/env python

from distutils.core import setup

setup(
    name="django-query-exchange",
    version="0.1",

    license="New BSD License",

    author='Alex Koshelev',
    author_email="daevaorn@gmail.com",

    url="http://github.com/daevaorn/django-query-exchange/",

    packages=[
        'query_exchange',
        'query_exchange.templatetags',
    ],

    description="Django application for handling GET query params for url creation",

    classifiers=[
        "Framework :: Django",
        "License :: OSI Approved :: BSD License",
    ]
)
