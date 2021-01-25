# Generated by Django 3.1.4 on 2021-01-25 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_app', '0009_links'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='dnb_link',
            field=models.CharField(default='/', max_length=255),
        ),
        migrations.AddField(
            model_name='company',
            name='glassdoor_link',
            field=models.CharField(default='/', max_length=255),
        ),
        migrations.AddField(
            model_name='company',
            name='google_link',
            field=models.CharField(default='/', max_length=255),
        ),
        migrations.AddField(
            model_name='company',
            name='indeed_link',
            field=models.CharField(default='/', max_length=255),
        ),
        migrations.DeleteModel(
            name='Links',
        ),
    ]