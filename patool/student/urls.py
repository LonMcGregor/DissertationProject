from django.conf.urls import include, url

from . import views

urlpatterns = [
    url('', include('django.contrib.auth.urls')),
    url('cw/(?P<singlecw>[0-9a-zA-Z]*)/submit', views.upload_solution),
    url('pushtest', views.push_test),
    #url('cw', views.select_coursework),
    url('cw/(?P<singlecw>[0-9a-zA-Z]*)', views.detail_coursework),
    url(r'^$', views.index, name='index'),
]
