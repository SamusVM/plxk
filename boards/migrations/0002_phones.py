# Generated by Django 2.0 on 2017-12-12 12:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('boards', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Phones',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('n_main', models.CharField(max_length=4)),
                ('n_second', models.CharField(max_length=4)),
                ('n_mobile', models.CharField(max_length=4)),
                ('n_out', models.CharField(max_length=11)),
                ('mobile1', models.CharField(max_length=11)),
                ('mobile2', models.CharField(max_length=11)),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pones', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
