# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-06 23:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20170406_0136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='tags',
            field=models.ManyToManyField(related_name='blogs', related_query_name='blog', to='blog.Tag'),
        ),
    ]
