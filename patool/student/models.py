from django.db import models

# Create your models here.

class StoredSolution(models.Model):
    file = models.FileField(upload_to='solutions/coursework/userid')