# Generated by Django 3.1.4 on 2021-05-13 08:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0005_sub_product_type'),
        ('correspondence', '0020_auto_20210323_1518'),
        ('edms', '0145_auto_20210412_1129'),
    ]

    operations = [
        migrations.AddField(
            model_name='doc_type_phase',
            name='doc_type_version',
            field=models.CharField(max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='doc_type_phase_queue',
            name='doc_type_version',
            field=models.CharField(max_length=2, null=True),
        ),
        migrations.CreateModel(
            name='Doc_Sub_Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='sub_product_type', to='edms.document')),
                ('sub_product_type', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='documents', to='production.sub_product_type')),
            ],
        ),
        migrations.CreateModel(
            name='Doc_Scope',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='scope', to='edms.document')),
                ('scope', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='documents', to='production.scope')),
            ],
        ),
        migrations.CreateModel(
            name='Doc_Law',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='law', to='edms.document')),
                ('law', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='documents', to='correspondence.law')),
            ],
        ),
        migrations.CreateModel(
            name='Client_Requirements',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=10)),
                ('bag_name', models.CharField(blank=True, max_length=100, null=True)),
                ('weight_kg', models.CharField(blank=True, max_length=10, null=True)),
                ('mf_water', models.CharField(blank=True, max_length=10, null=True)),
                ('mf_ash', models.CharField(blank=True, max_length=10, null=True)),
                ('mf_evaporable', models.CharField(blank=True, max_length=10, null=True)),
                ('mf_not_evaporable_carbon', models.CharField(blank=True, max_length=10, null=True)),
                ('main_faction', models.CharField(blank=True, max_length=10, null=True)),
                ('granulation_lt5', models.CharField(blank=True, max_length=10, null=True)),
                ('granulation_lt10', models.CharField(blank=True, max_length=10, null=True)),
                ('granulation_lt20', models.CharField(blank=True, max_length=10, null=True)),
                ('granulation_lt25', models.CharField(blank=True, max_length=10, null=True)),
                ('granulation_lt40', models.CharField(blank=True, max_length=10, null=True)),
                ('granulation_mt20', models.CharField(blank=True, max_length=10, null=True)),
                ('granulation_mt60', models.CharField(blank=True, max_length=10, null=True)),
                ('granulation_mt80', models.CharField(blank=True, max_length=10, null=True)),
                ('appearance', models.CharField(blank=True, max_length=10, null=True)),
                ('color', models.CharField(blank=True, max_length=10, null=True)),
                ('density', models.CharField(blank=True, max_length=10, null=True)),
                ('mf_basic', models.CharField(blank=True, max_length=10, null=True)),
                ('mf_ethanol', models.CharField(blank=True, max_length=10, null=True)),
                ('mf_acids', models.CharField(blank=True, max_length=10, null=True)),
                ('mf_not_evaporable_residue', models.CharField(blank=True, max_length=10, null=True)),
                ('smell', models.CharField(blank=True, max_length=10, null=True)),
                ('color_APHA', models.CharField(blank=True, max_length=10, null=True)),
                ('dry_residue', models.CharField(blank=True, max_length=10, null=True)),
                ('mf_ethanol_ppm', models.CharField(blank=True, max_length=10, null=True)),
                ('methanol_ppm', models.CharField(blank=True, max_length=10, null=True)),
                ('isopropanol_ppm', models.CharField(blank=True, max_length=10, null=True)),
                ('benzol_ppm', models.CharField(blank=True, max_length=10, null=True)),
                ('toluene_ppm', models.CharField(blank=True, max_length=10, null=True)),
                ('ethylmethyl_ketone_ppm', models.CharField(blank=True, max_length=10, null=True)),
                ('other_identified_impurities_ppm', models.CharField(blank=True, max_length=10, null=True)),
                ('unidentified_impurities_ppm', models.CharField(blank=True, max_length=10, null=True)),
                ('brand_of_resin', models.CharField(blank=True, max_length=10, null=True)),
                ('mf_dry_residue', models.CharField(blank=True, max_length=10, null=True)),
                ('mf_free_formaldehyde', models.CharField(blank=True, max_length=10, null=True)),
                ('conditional_viscosity', models.CharField(blank=True, max_length=10, null=True)),
                ('hydrogen_ions', models.CharField(blank=True, max_length=10, null=True)),
                ('gelatinization_time', models.CharField(blank=True, max_length=10, null=True)),
                ('miscibility_with_water', models.CharField(blank=True, max_length=10, null=True)),
                ('warranty_period', models.CharField(blank=True, max_length=10, null=True)),
                ('TU', models.CharField(blank=True, max_length=10, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='client_requirements', to='edms.document')),
            ],
        ),
    ]
