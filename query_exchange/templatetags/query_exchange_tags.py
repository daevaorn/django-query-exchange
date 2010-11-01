import re

from django import template
from django.utils.datastructures import MultiValueDict
from django.template.defaulttags import URLNode
from django.utils.html import escape

from query_exchange import process_query

register = template.Library()

# Regex for URL arguments including filters
url_arg_re = re.compile(
    r"(?:(%(name)s)=)?(%(value)s(?:\|%(name)s(?::%(value)s)?)*)" % {
        'name':'\w+',
        'value':'''(?:(?:'[^']*')|(?:"[^"]*")|(?:[\w\.-]+))'''},
    re.VERBOSE)

class BaseQueryNode(object):
    def render(self, context):
        url, extra_params = self.get_url(context)

        if 'request' not in context:
            raise ValueError('`request` needed in context for GET query processing')

        params = MultiValueDict(context['request'].GET.iterlists())
        params.update(MultiValueDict(extra_params))

        query = process_query(
            params,
            self.keep and [v.resolve(context) for v in self.keep],
            self.exclude and [v.resolve(context) for v in self.exclude],
            self.add and dict([(k, v.resolve(context)) for k, v in self.add.iteritems()]),
        )
        if query:
            url += '?' + query

        url = escape(url)

        if self._asvar:
            context[self._asvar] = url
            return ''
        else:
            return url

class URLWithQueryNode(BaseQueryNode, URLNode):
    def __init__(self, view_name, args, kwargs, asvar, keep, exclude, add):
        super(URLWithQueryNode, self).__init__(view_name, args, kwargs, None)
        self._asvar = asvar

        self.keep = keep
        self.exclude = exclude
        self.add = add

    def get_url(self, context):
        try:
            self.view_name = self.view_name.resolve(context)
        except AttributeError:
            pass

        return URLNode.render(self, context), {}

class WithQueryNode(BaseQueryNode, template.Node):
    def __init__(self, url, asvar, keep, exclude, add):
        self.url = url
        self._asvar = asvar

        self.keep = keep
        self.exclude = exclude
        self.add = add

    def get_url(self, context):
        from cgi import parse_qs

        url = self.url.resolve(context)
        if '?' in url:
            url, params = url.split('?', 1)

            return url, parse_qs(params)

        return url, {}

def parse_args(parser, bit):
    end = 0
    args = []
    kwargs = {}

    for i, match in enumerate(url_arg_re.finditer(bit)):
        if (i == 0 and match.start() != 0) or \
              (i > 0 and (bit[end:match.start()] != ',')):
            raise template.TemplateSyntaxError("Malformed arguments to url tag")
        end = match.end()
        name, value = match.group(1), match.group(2)
        if name:
            kwargs[name] = parser.compile_filter(value)
        else:
            args.append(parser.compile_filter(value))
    if end != len(bit):
        raise template.TemplateSyntaxError("Malformed arguments to url tag")

    return args, kwargs

@register.tag
def url_with_query(parser, token):
    bits = token.split_contents()
    if len(bits) < 2:
        raise template.TemplateSyntaxError("'%s' takes at least one argument"
                                           " (path to a view)" % bits[0])
    viewname = parser.compile_filter(bits[1])
    args = []
    kwargs = {}
    asvar = None

    keep = None
    exclude = None
    add = None

    if len(bits) > 2:
        bits = iter(bits[2:])
        for bit in bits:
            if bit == 'as':
                asvar = bits.next()
                break
            elif bit == 'keep':
                keep, _ = parse_args(parser, bits.next())
            elif bit == 'exclude':
                exclude, _ = parse_args(parser, bits.next())
            elif bit == 'add':
                _, add = parse_args(parser, bits.next())
            else:
                args, kwargs = parse_args(parser, bit)

    return URLWithQueryNode(viewname, args, kwargs, asvar, keep, exclude, add)


@register.tag
def with_query(parser, token):
    bits = token.split_contents()
    if len(bits) < 2:
        raise template.TemplateSyntaxError("'%s' takes at least one argument"
                                           " (path to a view)" % bits[0])
    url = parser.compile_filter(bits[1])
    asvar = None

    keep = None
    exclude = None
    add = None

    if len(bits) > 2:
        bits = iter(bits[2:])
        for bit in bits:
            if bit == 'as':
                asvar = bits.next()
                break
            elif bit == 'keep':
                keep, _ = parse_args(parser, bits.next())
            elif bit == 'exclude':
                exclude, _ = parse_args(parser, bits.next())
            elif bit == 'add':
                _, add = parse_args(parser, bits.next())

    return WithQueryNode(url, asvar, keep, exclude, add)
