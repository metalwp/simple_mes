# Generated by Django 3.0.7 on 2020-09-04 14:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('station_manager', '0001_initial'),
        ('bom_manager', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProcessRoute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('c_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('m_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='是否删除')),
                ('name', models.CharField(max_length=100, verbose_name='工艺路线名称')),
                ('remark', models.CharField(blank=True, max_length=200, null=True, verbose_name='备注')),
            ],
            options={
                'verbose_name': '工艺路线',
                'verbose_name_plural': '工艺路线',
                'db_table': 'sm_process_route',
                'unique_together': {('is_delete', 'name')},
            },
        ),
        migrations.CreateModel(
            name='ProcessStep',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('c_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('m_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='是否删除')),
                ('name', models.CharField(max_length=100, verbose_name='工序名称')),
                ('sequence_no', models.SmallIntegerField(blank=True, default=None, null=True, verbose_name='工序顺序号')),
                ('process_lock', models.BooleanField(default=False, verbose_name='工序互锁')),
                ('remark', models.CharField(blank=True, max_length=200, null=True, verbose_name='备注')),
                ('fixture', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='station_manager.Fixture', verbose_name='工装')),
                ('process_route', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='process_manager.ProcessRoute', verbose_name='工艺路线')),
                ('relate_material', models.ManyToManyField(blank=True, to='bom_manager.MaterialModel', verbose_name='关联物料')),
            ],
            options={
                'verbose_name': '工序',
                'verbose_name_plural': '工序',
                'db_table': 'sm_process_step',
                'unique_together': {('is_delete', 'sequence_no', 'process_route')},
            },
        ),
    ]
