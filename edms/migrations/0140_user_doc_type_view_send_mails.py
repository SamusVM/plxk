# Generated by Django 3.1.4 on 2021-02-01 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edms', '0139_auto_20210127_1058'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_doc_type_view',
            name='send_mails',
            field=models.BooleanField(default=False),
        ),
    ]
