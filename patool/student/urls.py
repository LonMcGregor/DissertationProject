from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views
from . import fileviewer

urlpatterns = [
    url('login', auth_views.login, name='login'),
    url('logout', auth_views.logout, name='logout'),
    url('cw/(?P<cw>[0-9a-zA-Z\-_]*)/solution', views.upload_solution, name='solution'),
    url('cw/(?P<cw>[0-9a-zA-Z\-_]*)/test', views.upload_test, name='test'),
    url('cw/(?P<cw>[0-9a-zA-Z\-_]*)/submit', views.upload_submission, name='submit'),
    url('cw/feedback/(?P<test_match>[0-9a-zA-Z\-_]*)', views.feedback, name='feedback'),
    url('cw/(?P<cw>[0-9a-zA-Z\-_]*)/make_tm', views.create_new_test_match, name='make_tm_student'),
    url('cw/(?P<cw>[0-9a-zA-Z\-_]*)', views.detail_coursework, name='cw'),
    url('delsub/(?P<sub>[0-9a-zA-Z\-_]*)', views.delete_submission, name='delsub'),
    url('file/(?P<sub_id>[0-9a-zA-Z\-_]*)/(?P<filename>[0-9a-zA-Z\-_.]*)',
        fileviewer.download_file, name='download_file'),
    url(r'^$', views.index, name='student_index'),
]
