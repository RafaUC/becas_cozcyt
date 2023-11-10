import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'becas_cozcyt.settings')
django.setup()
from django.db import migrations, models, connection
import csv
import sys
from usuarios.models import Estado, Municipio, Institucion, Carrera   # Importa el modelo de tu base de datos

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'becas_cozcyt.settings')
django.setup()

def load_data_from_sql(sqlFile):
    print(f'Importando "{sqlFile}".')
    file_path = os.path.join(os.path.dirname(__file__), sqlFile)
    sql_statement = open(file_path).read()
    #print(sql_statement)
    with connection.cursor() as c:
        c.execute(sql_statement)
    with connection.cursor() as c:
        c.execute('UNLOCK TABLES;')
    print(f'Importado "{sqlFile}" con exito.')


def importar_datos_desde_csv(archivo_csv, modelo, mapeo_campos):
    print(f'Importando "{archivo_csv}".')
    with open(archivo_csv, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            datos_a_guardar = {}
            for campo, columna_csv in mapeo_campos.items():                                              
                datos_a_guardar[campo] = row.get(columna_csv)
            
            nuevo_registro = modelo(**datos_a_guardar)        
            nuevo_registro.save()
            sys.stdout.write(".")  # Imprime un punto sin salto de línea
            sys.stdout.flush()
    print(' ')
    print(f'Importado "{archivo_csv}" con exito.')


importar_datos_desde_csv('catalogos/CatalogoInegiEstatal.csv', Estado, {
    'id': 'CVE_ENT',
    'nombre': 'NOM_ENT'
})
importar_datos_desde_csv('catalogos/CatalogoInegiMunicipal.csv', Municipio, {
    'cve_mun': 'CVE_MUN',
    'estado_id': 'CVE_ENT',
    'nombre': 'NOM_MUN'
})
importar_datos_desde_csv('catalogos/institutos.csv', Institucion, {
    'id': 'id',
    'nombre': 'instituto',
    'puntos': 'puntos'
})
importar_datos_desde_csv('catalogos/carreras.csv', Carrera, {
    'institucion_id': 'instituto',
    'nombre': 'carrera',
    'puntos': 'puntos'
})
load_data_from_sql('catalogos/estudioSE.sql')
load_data_from_sql('catalogos/puntos_municipios.sql')


""""
class Migration(migrations.Migration):
    dependencies = [
        ('..', '...'),
    ]

    operations = [
        migrations.RunPython(load_data_from_sql),
    ]
    """