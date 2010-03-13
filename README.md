## Installation

Add `query_exchange` to INSTALLED_APPS in your `settings.py`:

    INSTALLLED_APPS = (
        # ...

        'query_exchange',
    )

## Usage

### In python code

`query_exchange` has `reverse_with_query` function that reverts url by view name, args and additional query string params

Assumes there is this url config:

     urlpatterns = patterns(
         url('^cinema/(\w+)/$', views.cinema, name='cinema_view')
     )

And it is required to build url to 'cinema_view' with additional date parameter

     from query_exchange import reverse_with_query

     url = reverse_with_query('cinema_view', args=('luxor',), add={'date': '2010-03-12'}, params=request.GET)

the result will be

     /cinema/luxor/?date=2010-03-12

### In templates

Before using template tags you have to load correspondent tags library
 
    {% load query_exchange_tags %}