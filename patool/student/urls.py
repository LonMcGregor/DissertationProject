from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url('login', auth_views.login, name='login'),
    url('logout', auth_views.logout, name='logout'),
    url('cw/(?P<cw>[0-9a-zA-Z\-_]*)/solution', views.upload_solution, name='solution'),
    url('cw/(?P<cw>[0-9a-zA-Z\-_]*)/test', views.upload_solution, name='test'),
    url('cw/feedback/(?P<test_match>[0-9a-zA-Z\-_]*)', views.feedback, name='feedback'),
    url('cw/(?P<cw>[0-9a-zA-Z\-_]*)/make_tm', views.create_test_match, name='make_tm_student'),
    url('cw/(?P<cw>[0-9a-zA-Z\-_]*)/make_ptm', views.create_personal_test_match,
        name='make_ptm_student'),
    url('cw/(?P<cw>[0-9a-zA-Z\-_]*)', views.detail_coursework, name='cw'),
    url('file/(?P<sub_id>[0-9a-zA-Z\-_]*)/(?P<filename>[0-9a-zA-Z\-_.]*)',
        views.download_file, name='download_file'),
    url('setfinal/(?P<sub_id>[0-9a-zA-Z\-_]*)', views.set_final, name='set_final_sub'),
    url(r'^$', views.index, name='student_index'),
]
