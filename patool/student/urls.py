from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url('login', auth_views.login, name='login'),
    url('logout', auth_views.logout, name='logout'),
    url('cw/(?P<cw>[0-9a-zA-Z\-_]*)/solution', views.upload_solution, name='solution'),
    url('cw/(?P<cw>[0-9a-zA-Z\-_]*)/test/(?P<tid>[0-9a-zA-Z\-_]*)', views.upload_test, name='test'),
    url('cw/(?P<cw>[0-9a-zA-Z\-_]*)/make_tm', views.create_new_test_match, name='make_tm_student'),
    url('cw/(?P<cw>[0-9a-zA-Z\-_]*)', views.detail_coursework, name='cw'),
    url('delsub', views.delete_submission, name='delsub'),
    url(r'^$', views.index, name='student_index'),
]
