# Generated by Django 4.1.7 on 2024-05-07 16:08

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('modalidades', '0009_modificar_convocatoria'),
    ]

    operations = [
        migrations.AlterField(
            model_name='convocatoria',
            name='fecha_nuevo_ciclo',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
