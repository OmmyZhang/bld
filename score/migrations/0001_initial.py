# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-07-04 07:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='record',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=50)),
                ('detail', models.CharField(max_length=200)),
                ('who', models.CharField(max_length=50)),
                ('when', models.DateField()),
                ('soc', models.IntegerField(default=0)),
            ],
        ),
    ]
