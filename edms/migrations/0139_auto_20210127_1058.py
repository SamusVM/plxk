# Generated by Django 3.1.4 on 2021-01-27 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edms', '0138_user_doc_type_view'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mark_demand',
            name='comment',
            field=models.CharField(blank=True, max_length=5000, null=True),
        ),
    ]