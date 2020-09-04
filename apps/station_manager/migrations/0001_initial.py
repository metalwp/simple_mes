# Generated by Django 3.0.7 on 2020-09-04 14:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Station',
            fields=[
                ('c_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('m_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='是否删除')),
                ('num', models.CharField(max_length=32, primary_key=True, serialize=False, verbose_name='工站编号')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='工站名称')),
                ('category', models.PositiveSmallIntegerField(choices=[(0, '无'), (1, '组装'), (2, '测试'), (3, '标定'), (4, '检验'), (5, '其他')], default=0, verbose_name='工位类型')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP地址')),
                ('remarks', models.CharField(blank=True, max_length=100, null=True, verbose_name='备注')),
            ],
            options={
                'verbose_name': '工站信息',
                'verbose_name_plural': '工站信息',
                'db_table': 'sm_station',
                'unique_together': {('is_delete', 'num')},
            },
        ),
        migrations.CreateModel(
            name='Fixture',
            fields=[
                ('c_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('m_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='是否删除')),
                ('num', models.CharField(max_length=20, primary_key=True, serialize=False, unique=True, verbose_name='工装编号')),
                ('name', models.CharField(max_length=20, unique=True, verbose_name='工装名称')),
                ('remarks', models.CharField(blank=True, max_length=100, null=True, verbose_name='备注')),
                ('station', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='station_manager.Station', verbose_name='工站')),
            ],
            options={
                'verbose_name': '工装',
                'verbose_name_plural': '工装',
                'db_table': 'sm_fixture',
                'unique_together': {('is_delete', 'num'), ('is_delete', 'name')},
            },
        ),
        migrations.CreateModel(
            name='TestStandard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('c_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('m_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='是否删除')),
                ('num', models.PositiveIntegerField(verbose_name='测试项编号')),
                ('name', models.CharField(max_length=20, verbose_name='测试项名称')),
                ('upper', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='上限')),
                ('lower', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='下限')),
                ('version', models.CharField(max_length=10, verbose_name='版本')),
                ('fixture', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='station_manager.Fixture', verbose_name='工装')),
            ],
            options={
                'verbose_name': '测试标准',
                'verbose_name_plural': '测试标准',
                'db_table': 'sm_teststandard',
                'unique_together': {('is_delete', 'fixture', 'version', 'num')},
            },
        ),
    ]
