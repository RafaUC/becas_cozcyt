# Generated by Django 4.1.7 on 2024-05-06 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mensajes', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificacion',
            name='titulo',
            field=models.CharField(blank=True, default='Departamento de becas COZCYT ', max_length=255, null=True),
        ),
    ]
