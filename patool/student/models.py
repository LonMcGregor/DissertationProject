from django.db import models

# Create your models here.
def user_directory_path(instance, filename):
    return 'solutions/%s/%s/%s' % (instance.cwid, instance.userid, filename)


class StoredSolution(models.Model):
    file = models.FileField(upload_to=user_directory_path)
    cwid = models.CharField(max_length=16, default="")
    userid = models.CharField(max_length=32, default="")


