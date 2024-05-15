# Generated by Django 4.1.7 on 2024-03-04 20:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Elemento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255, verbose_name='Nombre')),
                ('obligatorio', models.BooleanField(default=True, verbose_name='Obligatorio')),
                ('opcionOtro', models.BooleanField(default=True, verbose_name='Opcion Otro')),
                ('numMin', models.PositiveIntegerField(default=0, verbose_name='numMin')),
                ('numMax', models.PositiveIntegerField(default=10, verbose_name='numMax')),
                ('row', models.IntegerField(default=100000, verbose_name='row')),
                ('col', models.IntegerField(default=100000, verbose_name='col')),
                ('tipo', models.CharField(choices=[('separador', 'Separador'), ('numerico', 'Numérico'), ('texto_corto', 'Texto Corto'), ('texto_parrafo', 'Texto Párrafo'), ('hora', 'Hora'), ('fecha', 'Fecha'), ('opcion_multiple', 'Opción Múltiple'), ('casillas', 'Casillas'), ('desplegable', 'Desplegable')], max_length=20, verbose_name='Tipo')),
            ],
            options={
                'verbose_name': 'Elemento',
                'verbose_name_plural': 'Elementos',
                'ordering': ['seccion', 'row', 'col'],
            },
        ),
        migrations.CreateModel(
            name='Opcion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255, verbose_name='Nombre Opción')),
                ('orden', models.IntegerField(default=100000, verbose_name='orden')),
            ],
            options={
                'verbose_name': 'Opción',
                'verbose_name_plural': 'Opciones',
                'ordering': ['elemento', 'orden'],
            },
        ),
        migrations.CreateModel(
            name='RAgregacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Respuesta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('elemento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='estudio_socio_economico.elemento')),
                ('rAgregacion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='estudio_socio_economico.ragregacion')),
            ],
            options={
                'verbose_name': 'Respuesta',
                'verbose_name_plural': 'Respuestas',
            },
        ),
        migrations.CreateModel(
            name='Seccion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('tipo', models.CharField(choices=[('unico', 'Único'), ('agregacion', 'Agregación')], max_length=10)),
                ('orden', models.IntegerField(default=100000, verbose_name='orden')),
            ],
            options={
                'ordering': ['orden'],
            },
        ),
        migrations.CreateModel(
            name='RCasillas',
            fields=[
                ('respuesta_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='estudio_socio_economico.respuesta')),
                ('otro', models.CharField(blank=True, max_length=255, null=True, verbose_name='Otro')),
            ],
            bases=('estudio_socio_economico.respuesta',),
        ),
        migrations.CreateModel(
            name='RDesplegable',
            fields=[
                ('respuesta_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='estudio_socio_economico.respuesta')),
                ('otro', models.CharField(blank=True, max_length=255, null=True, verbose_name='Otro')),
            ],
            bases=('estudio_socio_economico.respuesta',),
        ),
        migrations.CreateModel(
            name='RFecha',
            fields=[
                ('respuesta_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='estudio_socio_economico.respuesta')),
                ('fecha', models.DateField(blank=True, null=True)),
            ],
            bases=('estudio_socio_economico.respuesta',),
        ),
        migrations.CreateModel(
            name='RHora',
            fields=[
                ('respuesta_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='estudio_socio_economico.respuesta')),
                ('hora', models.TimeField(blank=True, null=True)),
            ],
            bases=('estudio_socio_economico.respuesta',),
        ),
        migrations.CreateModel(
            name='RNumerico',
            fields=[
                ('respuesta_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='estudio_socio_economico.respuesta')),
                ('valor', models.CharField(blank=True, max_length=255, null=True)),
            ],
            bases=('estudio_socio_economico.respuesta',),
        ),
        migrations.CreateModel(
            name='ROpcionMultiple',
            fields=[
                ('respuesta_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='estudio_socio_economico.respuesta')),
                ('otro', models.CharField(blank=True, max_length=255, null=True, verbose_name='Otro')),
            ],
            bases=('estudio_socio_economico.respuesta',),
        ),
        migrations.CreateModel(
            name='RTextoCorto',
            fields=[
                ('respuesta_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='estudio_socio_economico.respuesta')),
                ('texto', models.CharField(blank=True, max_length=255, null=True)),
            ],
            bases=('estudio_socio_economico.respuesta',),
        ),
        migrations.CreateModel(
            name='RTextoParrafo',
            fields=[
                ('respuesta_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='estudio_socio_economico.respuesta')),
                ('texto', models.TextField(blank=True, null=True)),
            ],
            bases=('estudio_socio_economico.respuesta',),
        ),
    ]
