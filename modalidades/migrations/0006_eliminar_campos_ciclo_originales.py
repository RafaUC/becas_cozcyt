# Generated by Django 4.1.7 on 2024-05-06 18:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('modalidades', '0005_migracion_ciclos_a_FK'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='convocatoria',
            name='ultimo_ciclo_publicado',
        ),
    ]
