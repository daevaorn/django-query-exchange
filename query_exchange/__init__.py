from django.utils.http import urlencode
from django.core.urlresolvers import reverse


def reverse_with_query(viewname, urlconf=None, args=None, kwargs=None, prefix=None, current_app=None,
                       params=None, keep=None, exclude=None, add=None):
    url = reverse(viewname, urlconf, args, kwargs, prefix, current_app)

    if params:
        url += '?' + process_query(params, keep, exclude, add)

    return url


def process_query(params, keep=None, exclude=None, add=None):
    if hasattr(params, 'iterlists'):
        data = dict(params.iterlists())
    else:
        data = dict((k, isinstance(v, list) and v or [v]) for k, v in params.iteritems())

    if keep:
        data = dict([(k, v) for k, v in data.iteritems() if k in keep])
    elif exclude:
        data = dict([(k, v) for k, v in data.iteritems() if k not in exclude])

    if add:
        if hasattr(add, 'iterlists'):
            data.update(dict(add.iterlists()))
        else:
            data.update(dict([(k, [v]) for k, v in add.iteritems()]))

    return urlencode([(k, v) for k, l in data.iteritems() for v in l])
