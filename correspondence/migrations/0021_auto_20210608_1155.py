# Generated by Django 3.1.4 on 2021-06-08 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('correspondence', '0020_auto_20210323_1518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='author_comment',
            field=models.CharField(blank=True, max_length=5000, null=True),
        ),
    ]
