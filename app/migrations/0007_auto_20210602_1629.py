# Generated by Django 2.2 on 2021-06-02 21:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20210601_2219'),
    ]

    operations = [
        migrations.AlterField(
            model_name='extrapoint',
            name='ex_point',
            field=models.DecimalField(decimal_places=2, max_digits=4),
        ),
        migrations.AlterField(
            model_name='point',
            name='earned',
            field=models.DecimalField(decimal_places=2, max_digits=5),
        ),
        migrations.AlterField(
            model_name='pointrate',
            name='rate',
            field=models.DecimalField(decimal_places=2, max_digits=4),
        ),
    ]
