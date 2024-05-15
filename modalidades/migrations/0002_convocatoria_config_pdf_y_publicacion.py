# Generated by Django 4.1.7 on 2024-05-03 20:00

from django.db import migrations, models
import modalidades.models


class Migration(migrations.Migration):

    dependencies = [
        ('modalidades', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='convocatoria',
            name='archivo_convocatoria',
            field=models.FileField(null=True, upload_to=modalidades.models.modalidadMediaPath, validators=[modalidades.models.validador_pdf], verbose_name='Convocatoria'),
        ),
        migrations.AddField(
            model_name='convocatoria',
            name='ultimo_ciclo_publicado',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Ultimo ciclo publicado'),
        ),
    ]
