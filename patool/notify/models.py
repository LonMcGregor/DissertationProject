from django.contrib.auth.models import User
from django.db import models as m


class MessageTemplate(m.Model):
    content = m.CharField(max_length=512)
    link = m.CharField(max_length=512)


class Message(m.Model):
    template = m.ForeignKey(MessageTemplate)
    rel = m.CharField(max_length=256)
    user = m.ForeignKey(User)
    has_been_read = m.BooleanField()
    has_been_deleted = m.BooleanField()
