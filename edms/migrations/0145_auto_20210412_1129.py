# Generated by Django 3.1.4 on 2021-04-12 08:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('edms', '0144_auto_20210406_1531'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mark_demand',
            name='employee_seat_control',
        ),
        migrations.AddField(
            model_name='mark_demand',
            name='delegated_from',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='delegated', to='edms.employee_seat'),
        ),
    ]
