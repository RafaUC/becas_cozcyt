# Generated by Django 4.1.7 on 2024-03-04 20:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('solicitudes', '0001_initial'),
        ('usuarios', '0001_initial'),
        ('modalidades', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitud',
            name='solicitante',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.solicitante'),
        ),
        migrations.AddField(
            model_name='respuestadocumento',
            name='documento',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='modalidades.documento'),
        ),
        migrations.AddField(
            model_name='respuestadocumento',
            name='solicitud',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='solicitudes.solicitud'),
        ),
        migrations.AlterUniqueTogether(
            name='solicitud',
            unique_together={('modalidad', 'ciclo', 'solicitante')},
        ),
        migrations.AlterUniqueTogether(
            name='respuestadocumento',
            unique_together={('solicitud', 'documento')},
        ),
    ]
