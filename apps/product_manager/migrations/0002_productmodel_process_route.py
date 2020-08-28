# Generated by Django 3.0.7 on 2020-08-28 10:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('process_manager', '0001_initial'),
        ('product_manager', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='productmodel',
            name='process_route',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='process_manager.ProcessRoute', verbose_name='工艺路线'),
        ),
    ]
