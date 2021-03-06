# Generated by Django 3.1.4 on 2021-07-13 06:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0031_userprofile_scope_add'),
        ('production', '0005_sub_product_type'),
        ('boards', '0009_auto_20210323_1515'),
    ]

    operations = [
        migrations.CreateModel(
            name='Non_compliance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phase', models.PositiveSmallIntegerField()),
                ('dep_chief_approved', models.BooleanField(null=True)),
                ('date_added', models.DateField(auto_now_add=True)),
                ('name', models.CharField(max_length=100)),
                ('party_number', models.CharField(max_length=10)),
                ('order_number', models.CharField(max_length=10)),
                ('manufacture_date', models.DateField()),
                ('total_quantity', models.CharField(max_length=5)),
                ('nc_quantity', models.CharField(max_length=5)),
                ('packing_type', models.CharField(max_length=15)),
                ('reason', models.CharField(max_length=300)),
                ('status', models.CharField(max_length=100)),
                ('classification', models.CharField(max_length=100)),
                ('defect', models.CharField(max_length=100)),
                ('analysis_results', models.CharField(max_length=100)),
                ('sector', models.CharField(max_length=100)),
                ('final_decision', models.CharField(max_length=100, null=True)),
                ('final_decision_time', models.DateTimeField(null=True)),
                ('corrective_action', models.CharField(max_length=100, null=True)),
                ('corrective_action_number', models.CharField(max_length=10, null=True)),
                ('retreatment_date', models.DateField(null=True)),
                ('spent_time', models.CharField(max_length=5, null=True)),
                ('people_involved', models.CharField(max_length=3, null=True)),
                ('quantity_updated', models.CharField(max_length=10, null=True)),
                ('status_updated', models.CharField(max_length=50, null=True)),
                ('return_date', models.DateField(null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='non_compliances_added', to='accounts.userprofile')),
                ('dep_chief', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='dep_non_compliances', to='accounts.userprofile')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='non_compliances', to='accounts.department')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='non_compliances', to='production.product_type')),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='non_compliances', to='boards.counterparty')),
                ('responsible', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='non_compliances_responsible', to='accounts.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='Non_compliance_comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.CharField(max_length=1000, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='non_compliance_comments', to='accounts.userprofile')),
                ('non_compliance', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='comments', to='boards.non_compliance')),
                ('original_comment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='answers', to='boards.non_compliance_comment')),
            ],
        ),
        migrations.CreateModel(
            name='Non_compliance_file',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='boards/non_compliances/%Y/%m')),
                ('name', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('non_compliance', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='files', to='boards.non_compliance')),
            ],
        ),
        migrations.CreateModel(
            name='Non_compliance_decision',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('decision', models.CharField(max_length=50, null=True)),
                ('decision_time', models.DateTimeField(null=True)),
                ('phase', models.SmallIntegerField(default=1)),
                ('is_active', models.BooleanField(default=True)),
                ('non_compliance', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='decisions', to='boards.non_compliance')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='non_compliance_decisions', to='accounts.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='Non_compliance_comment_file',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='boards/non_compliances/%Y/%m')),
                ('name', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='comment_files', to='boards.non_compliance_comment')),
            ],
        ),
    ]
