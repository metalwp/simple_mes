# Generated by Django 3.0.6 on 2020-05-22 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('process_manager', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='processstep',
            name='process_lock',
            field=models.BooleanField(default=False, verbose_name='工序互锁'),
        ),
    ]
