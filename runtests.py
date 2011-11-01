#!/usr/bin/env python
from django.conf import settings
from django.core.management import call_command

settings.configure(
    INSTALLED_APPS=('query_exchange',),
    DATABASES={'default':{'ENGINE': 'django.db.backends.sqlite3'}},
    ROOT_URLCONF='query_exchange.tests'
)

if __name__ == "__main__":
    call_command('test', 'query_exchange')
