# Generated by Django 4.1.7 on 2024-05-07 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modalidades', '0013_poblar_modelo_MontosModalidad'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='montomodalidad',
            options={'ordering': ['-id']},
        ),
        migrations.AlterField(
            model_name='montomodalidad',
            name='monto',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=7, verbose_name='Monto'),
        ),
        migrations.AlterUniqueTogether(
            name='montomodalidad',
            unique_together={('modalida', 'ciclo')},
        ),
    ]
