# Generated by Django 4.1.7 on 2024-05-07 16:22

from django.db import migrations

def poblarMontoModalidad(apps, schema_editor):
    Ciclo = apps.get_model('modalidades', 'Ciclo')    
    Modalidad = apps.get_model('modalidades', 'Modalidad')
    MontoModalidad = apps.get_model('modalidades', 'MontoModalidad')

    ciclos = Ciclo.objects.all()
    modadlidades = Modalidad.objects.all()
    for ciclo in ciclos:        
        for modalidad in modadlidades:
            MontoModalidad.objects.create(modalida=modalidad, ciclo=ciclo, monto=modalidad.monto)

class Migration(migrations.Migration):

    dependencies = [
        ('modalidades', '0012_crear_montosModalidad'),
    ]

    operations = [
        migrations.RunPython(poblarMontoModalidad),
    ]
