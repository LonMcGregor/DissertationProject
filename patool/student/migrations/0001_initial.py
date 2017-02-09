# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-09 17:41
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import student.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('name', models.CharField(max_length=128)),
                ('code', models.SlugField(max_length=32, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Coursework',
            fields=[
                ('id', models.SlugField(max_length=4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
                ('state', models.CharField(choices=[('i', 'Invisible to Students'), ('c', 'Closed for Submissions'), ('u', 'Accepting Uploads'), ('f', 'Accepting Feedback')], default='i', max_length=1)),
                ('file_pipe', models.CharField(max_length=128)),
                ('test_pipe', models.CharField(max_length=128)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student.Course')),
            ],
        ),
        migrations.CreateModel(
            name='EnrolledUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student.Course')),
                ('login', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=student.models.upload_directory_path)),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.SlugField(max_length=4, primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('s', 'Solution to Coursework'), ('c', 'Test Case for Solution'), ('r', 'Results of Running Test Case'), ('f', 'Feedback for a Solution'), ('d', 'Coursework Task Descriptor'), ('e', 'Executable that will act as Oracle'), ('i', 'Test to ensure Solution matches Interface')], max_length=1)),
                ('private', models.BooleanField()),
                ('coursework', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student.Coursework')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TestMatch',
            fields=[
                ('id', models.SlugField(max_length=4, primary_key=True, serialize=False)),
                ('error_level', models.IntegerField(null=True)),
                ('waiting_to_run', models.BooleanField()),
                ('visible_to_developer', models.BooleanField()),
                ('coursework', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tm_cw', to='student.Coursework')),
                ('feedback', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tm_fdbk_sub', to='student.Submission')),
                ('initiator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tm_init', to=settings.AUTH_USER_MODEL)),
                ('marker', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tm_marker', to=settings.AUTH_USER_MODEL)),
                ('result', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tm_res_sub', to='student.Submission')),
                ('solution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tm_sol_sub', to='student.Submission')),
                ('teacher_feedback', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tm_tfdbk_sub', to='student.Submission')),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tm_test_sub', to='student.Submission')),
            ],
        ),
        migrations.AddField(
            model_name='file',
            name='submission',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='student.Submission'),
        ),
        migrations.AlterUniqueTogether(
            name='enrolleduser',
            unique_together=set([('login', 'course')]),
        ),
    ]
