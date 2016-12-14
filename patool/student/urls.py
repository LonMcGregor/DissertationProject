from django.conf.urls import include, url

from . import views

urlpatterns = [
    url('', include('django.contrib.auth.urls')),
    url('upload', views.upload_solution),
    url('pushtest', views.push_test),
    url(r'^$', views.index, name='index'),
]
