from django.conf.urls import url
from django.urls import  path
from DjangoChat import views

urlpatterns = [
    # post views views.PostListView.as_view()
    url(r'^$', views.post_list, name='post_list'),
    url(r'^(?P<post_id>\d+)/share/$', views.post_share, name='post_share'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/'\
        r'(?P<post>[-\w]+)/like$', views.post_like, name = 'post_like'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/'\
        r'(?P<post>[-\w]+)/$',
        views.post_detail,
        name='post_detail'),

]