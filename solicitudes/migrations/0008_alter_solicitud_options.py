# Generated by Django 4.1.13 on 2024-05-29 20:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('solicitudes', '0007_renombrar_campos_ciclo_nuevos_2'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='solicitud',
            options={'ordering': ['-id'], 'verbose_name': 'Solicitud', 'verbose_name_plural': 'Solicitudes'},
        ),
    ]
