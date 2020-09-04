# Generated by Django 3.0.7 on 2020-09-04 14:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BOM',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('c_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('m_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='是否删除')),
                ('version', models.CharField(max_length=10, verbose_name='BOM版本')),
                ('remark', models.CharField(blank=True, max_length=200, null=True, verbose_name='备注')),
            ],
            options={
                'verbose_name': 'BOM',
                'verbose_name_plural': 'BOM',
                'db_table': 'sm_bom',
            },
        ),
        migrations.CreateModel(
            name='Bom_MaterialModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='用量')),
                ('is_traced', models.BooleanField(default=False, verbose_name='是否追溯')),
                ('bom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bom_manager.BOM')),
            ],
            options={
                'db_table': 'sm_bom_material_model',
            },
        ),
        migrations.CreateModel(
            name='MaterialModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('c_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('m_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='是否删除')),
                ('name', models.CharField(max_length=100, verbose_name='物料名称')),
                ('model', models.CharField(blank=True, max_length=200, null=True, verbose_name='型号描述')),
                ('erp_no', models.CharField(max_length=30, verbose_name='物料号')),
                ('category', models.SmallIntegerField(choices=[(0, '无'), (1, '钣金零件'), (2, '底盘总成'), (3, '电子电气'), (4, '金属标件'), (5, '塑料标件'), (6, '塑料零件'), (7, '其他')], default=0, verbose_name='类别')),
                ('bom', models.ManyToManyField(through='bom_manager.Bom_MaterialModel', to='bom_manager.BOM')),
            ],
            options={
                'verbose_name': '物料型号',
                'verbose_name_plural': '物料型号',
                'db_table': 'sm_material_model',
            },
        ),
        migrations.CreateModel(
            name='Inspection',
            fields=[
                ('c_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('m_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='是否删除')),
                ('num', models.CharField(max_length=20, primary_key=True, serialize=False, verbose_name='检验编号')),
                ('name', models.CharField(max_length=50, verbose_name='检验名称')),
                ('category', models.SmallIntegerField(choices=[(0, '无'), (1, '外观'), (2, '功能'), (3, '性能')], default=0, verbose_name='检验类型')),
                ('mode', models.SmallIntegerField(choices=[(0, '无'), (1, '目视'), (2, '测量工具'), (3, '手动设备'), (4, '自动设备')], default=0, verbose_name='检验方式')),
                ('upper', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='上限')),
                ('lower', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='下限')),
                ('material_model', models.ManyToManyField(blank=True, to='bom_manager.MaterialModel', verbose_name='物料型号')),
            ],
            options={
                'verbose_name': '检验项',
                'verbose_name_plural': '检验项',
                'db_table': 'sm_inspection',
            },
        ),
        migrations.AddField(
            model_name='bom_materialmodel',
            name='material_model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bom_manager.MaterialModel'),
        ),
    ]
