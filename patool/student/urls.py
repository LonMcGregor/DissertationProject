from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url('login', auth_views.login, name='login'),
    url('logout', auth_views.logout, name='logout'),
    url('cw/(?P<cw>[0-9a-zA-Z\-_]*)/solution', views.upload_solution, name='solution'),
    url('cw/(?P<cw>[0-9a-zA-Z\-_]*)/test', views.upload_solution, name='test'),
    url('cw/feedback/(?P<test_data>[0-9a-zA-Z\-_]*)', views.feedback, name='feedback'),
    url('cw/(?P<cw>[0-9a-zA-Z\-_]*)', views.detail_coursework, name='cw'),
    url('file/(?P<file_id>[0-9a-zA-Z\-_]*)/raw', views.show_file, name='show_file'),
    url('file/(?P<file_id>[0-9a-zA-Z\-_]*)/pretty', views.render_file, name='render_file'),
    url(r'^$', views.index, name='index'),
]
