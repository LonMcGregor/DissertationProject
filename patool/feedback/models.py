from django.contrib.auth.models import User
from django.db import models as m

import common.models as sm


# noinspection PyClassHasNoInit
class FeedbackGroup(m.Model):
    nickname = m.CharField(max_length=64)


# noinspection PyClassHasNoInit
class FeedbackMembership(m.Model):
    class Meta:
        unique_together = (('group', 'user'),)

    group = m.ForeignKey(FeedbackGroup, on_delete=m.CASCADE)
    user = m.ForeignKey(User, on_delete=m.CASCADE)
    nickname = m.CharField(max_length=32)


# noinspection PyClassHasNoInit
class FeedbackPlan(m.Model):
    class Meta:
        unique_together = (('group', 'coursework'),)

    group = m.ForeignKey(FeedbackGroup, on_delete=m.CASCADE)
    coursework = m.ForeignKey(sm.Coursework, on_delete=m.CASCADE)


# noinspection PyClassHasNoInit
class FeedbackForTestMatch(m.Model):
    class Meta:
        unique_together = (('group', 'test_match'),)

    test_match = m.ForeignKey(sm.TestMatch, on_delete=m.CASCADE)
    group = m.ForeignKey(FeedbackGroup, on_delete=m.CASCADE)
