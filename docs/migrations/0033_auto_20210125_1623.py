# Generated by Django 3.1.4 on 2021-01-25 14:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0008_counterparty_counterparty_certificate_counterparty_certificate_pause_counterparty_product'),
        ('docs', '0032_order_article_term'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='counterparty_link',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='contracts', to='boards.counterparty'),
        ),
        migrations.AddField(
            model_name='contract',
            name='incoterms',
            field=models.CharField(max_length=5000, null=True),
        ),
        migrations.AddField(
            model_name='contract',
            name='purchase_terms',
            field=models.CharField(max_length=5000, null=True),
        ),
    ]