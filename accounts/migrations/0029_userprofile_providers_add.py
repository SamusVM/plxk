# Generated by Django 3.1.4 on 2021-03-23 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0028_userprofile_access_to_all_contracts'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='providers_add',
            field=models.BooleanField(default=False),
        ),
    ]