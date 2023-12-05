import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'becas_cozcyt.settings')
django.setup()
from django.db import migrations, models, connection
import csv
import sys
from usuarios.models import Estado, Municipio, Institucion, Carrera, PuntajeGeneral, PuntajeMunicipio   # Importa el modelo de tu base de datos
from estudio_socio_economico.models import Seccion, Elemento, Opcion

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'becas_cozcyt.settings')
django.setup()



def load_data_from_sql(sqlFile):
    print(f'Importando "{sqlFile}".')
    try:
        file_path = os.path.join(os.path.dirname(__file__), sqlFile)        
        sql_statement = open(file_path).read()            
        with connection.cursor() as c:
            print(c.execute(sql_statement))                        
        with connection.cursor() as c:
            c.execute('UNLOCK TABLES;')             
        print(f'Terminado de importar "{sqlFile}".')
    except Exception as e:    
        print(f"Se produjo un error: {e} \nEs posible que los datos se hayan importado erroneamente.")
    

# el argumento mapeo campos es un diccionario donde la clave de 
# la isquierda es el el nombre atributo del modelo y el valor de la derecha es
# el nombre de la columna del csv al que corresponde
def importar_datos_desde_csv(archivo_csv, modelo, mapeo_campos):
    print(f'Importando "{archivo_csv}".')    
    with open(archivo_csv, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            datos_a_guardar = {}
            for campo, columna_csv in mapeo_campos.items():
                datos_a_guardar[campo] = row.get(columna_csv)

            nuevo_registro = modelo(**datos_a_guardar)

            try:
                nuevo_registro.save()
                sys.stdout.write('+')  # Imprime un símbolo de más para indicar éxito
            except Exception as e:
                sys.stdout.write('-')  # Imprime un símbolo de menos para indicar fallo                

            sys.stdout.flush()     
        print(f'Terminado de importar "{archivo_csv}".')
    


###Importacion de datos
while True:
    respuesta = input("Esto restablece la configuracion por defecto del Sistema. \n¿Proceder? (Sí/No): ").strip().lower()
    if respuesta in {'s', 'si'}:
        
        Estado.objects.all().delete()
        importar_datos_desde_csv('catalogos/CatalogoInegiEstatal.csv', Estado, {
            'id': 'CVE_ENT',
            'nombre': 'NOM_ENT'
        })
        Municipio.objects.all().delete()
        importar_datos_desde_csv('catalogos/CatalogoInegiMunicipal.csv', Municipio, {
            'cve_mun': 'CVE_MUN',
            'estado_id': 'CVE_ENT',
            'nombre': 'NOM_MUN'
        })
        Institucion.objects.all().delete()
        importar_datos_desde_csv('catalogos/institutos.csv', Institucion, {
            'id': 'id',
            'nombre': 'instituto',
            'puntos': 'puntos'
        })
        Carrera.objects.all().delete()
        importar_datos_desde_csv('catalogos/carreras.csv', Carrera, {
            'institucion_id': 'instituto',
            'nombre': 'carrera',
            'puntos': 'puntos'
        })
        PuntajeGeneral.objects.all().delete()
        importar_datos_desde_csv('catalogos/PuntajesGeneral.csv', PuntajeGeneral, {
            'id': 'id',
            'tipo': 'tipo',
            'nombre': 'nombre',
            'puntos': 'puntos'
        })
        
        Seccion.objects.all().delete()        
        Elemento.objects.all().delete()  
        Opcion.objects.all().delete()  
        load_data_from_sql('catalogos/estudioSE.sql')
        PuntajeMunicipio.objects.all().delete()
        load_data_from_sql('catalogos/puntos_municipios.sql')
        break
    elif respuesta in {'n', 'no'}:
        break
    else:        
        print("Respuesta no válida. Por favor, ingresa 'Sí' o 'No'.")



