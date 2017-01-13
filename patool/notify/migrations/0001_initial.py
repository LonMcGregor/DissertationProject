# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-13 12:00
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rel', models.CharField(max_length=256)),
                ('hasBeenRead', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='MessageTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=512)),
                ('link', models.CharField(max_length=512)),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notify.MessageTemplate'),
        ),
        migrations.AddField(
            model_name='message',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
