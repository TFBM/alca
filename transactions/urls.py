from django.conf.urls import patterns, url

urlpatterns = patterns('transactions.views',
    url(r'^/?$', 'transactions', name='transactions'),
    url(r'^new/?$', 'new', name='new'),
    url(r'^new/?$', 'new', name='new'),
)

