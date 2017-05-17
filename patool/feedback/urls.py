from django.conf.urls import url

from . import views

urlpatterns = [
    url('modify', views.modify, name='modify_feedback_group'),
    url('delete', views.delete, name='delete_feedback_group'),
]
