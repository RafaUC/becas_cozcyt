# Generated by Django 4.1.7 on 2024-05-06 18:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('solicitudes', '0004_solicitud_cambiar_default_test'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='solicitud',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='solicitud',
            name='ciclo',
        ),
    ]
