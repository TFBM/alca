from django.conf.urls import patterns, url

urlpatterns = patterns('transactions.views',
    url(r'^/?$', 'transactions', name='transactions'),
    url(r'^new/$', 'new', name='new'),
    url(r'^detail/(?P<id_transaction>\d+)/$', 'detail', name='detail'),
    url(r'^accept/(?P<id_transaction>\d+)/$', 'accept', name='accept'),
    url(r'^accept/(?P<id_transaction>\d+)/accept$', 'accept', name='accept'),
    url(r'^cancel/(?P<id_transaction>\d+)/$', 'cancel', name='cancel'),
)

