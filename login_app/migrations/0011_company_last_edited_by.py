# Generated by Django 3.1.4 on 2021-01-25 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_app', '0010_auto_20210125_0813'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='last_edited_by',
            field=models.CharField(default='Noone', max_length=255),
        ),
    ]
