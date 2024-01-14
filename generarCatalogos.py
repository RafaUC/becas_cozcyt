import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'becas_cozcyt.settings')
django.setup()
from django.db import migrations, models, connection
import csv
import sys
from usuarios.models import Solicitante, Estado, Municipio, Institucion, Carrera, PuntajeGeneral, PuntajeMunicipio   # Importa el modelo de tu base de datos
from estudio_socio_economico.models import Seccion, Elemento, Opcion
from modalidades.models import Modalidad
from solicitudes.models import Solicitud
import traceback
from mensajes import notificaciones as notif

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'becas_cozcyt.settings')
django.setup()



def load_data_from_sql(sqlFile):
    print(f'Importando "{sqlFile}".')    
    file_path = os.path.join(os.path.dirname(__file__), sqlFile)                        
    with open(file_path, 'r') as file:
        sql_statements = file.read().split(';')
        with connection.cursor() as c:
            for statement in sql_statements:
                statement = statement.strip()
                if statement: # Ignore empty statements                          
                    print(f'Sentencia sql: {statement[:80]}...')                 
                    try:
                        print(f'Registros afectados: {c.execute(statement)}')      
                    except Exception as e:    
                        print(f"Se produjo un error: {e}")
    with connection.cursor() as c:
        c.execute('UNLOCK TABLES;')             
    print(f'Terminado de importar "{sqlFile}".\n')
    
    

# el argumento mapeo campos es un diccionario donde la clave de 
# la isquierda es el el nombre atributo del modelo y el valor de la derecha es
# el nombre de la columna del csv al que corresponde
def importar_datos_desde_csv(archivo_csv, modelo, mapeo_campos, separador=','):
    print(f'Importando "{archivo_csv}".')    
    with open(archivo_csv, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=separador)
        for row in reader:
            datos_a_guardar = {}
            for campo, columna_csv in mapeo_campos.items():
                datos_a_guardar[campo] = row.get(columna_csv)
            #print(datos_a_guardar)            

            nuevo_registro = modelo(**datos_a_guardar)            
            #print(f'nuevo: {nuevo_registro} -- {nuevo_registro.id} -- {nuevo_registro.pk}')

            try:
                nuevo_registro.save()
                if nuevo_registro.id:
                    sys.stdout.write(f'+{nuevo_registro.id}')  # Imprime un símbolo de más para indicar éxito
                else:
                    sys.stdout.write(f'+ ')  # Imprime un símbolo de más para indicar éxito
            except Exception as e:                
                sys.stdout.write(f'-{nuevo_registro}')  # Imprime un símbolo de menos para indicar fallo                
                traceback.print_exc()
                

            sys.stdout.flush()     
        print(f'Terminado de importar "{archivo_csv}".')
    
def GenerarNotificacionesUsuarios(mensaje, archivo_csv, idHeader, separador=','):
    print(f'Notificando a usuarios del archivo "{archivo_csv}".')   
    with open(archivo_csv, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=separador)
        for row in reader:
            try:
                sid = row.get(idHeader)
                solicitante = Solicitante.objects.get(pk=sid)  
                notif.nueva(solicitante, mensaje, 'usuarios:perfil')
                sys.stdout.write(f'+m:{sid}')
            except Exception as e:                
                sys.stdout.write(f'-{sid}')  # Imprime un símbolo de menos para indicar fallo                
                traceback.print_exc()
        
            sys.stdout.flush()     
    


###Importacion de datos
while True:
    respuesta = input("Esto restablece la configuracion por defecto del Sistema, Tambien eliminara los registros de los usuarios. \n¿Proceder? (Sí/No): ").strip().lower()
    if respuesta in {'s', 'si'}:

        Seccion.objects.all().delete()        
        Elemento.objects.all().delete()  
        Opcion.objects.all().delete()  
        load_data_from_sql('catalogos/estudioSE.sql')

        #PuntajeMunicipio.objects.all().delete()
        load_data_from_sql('catalogos/puntos_municipios.sql')

        #Modalidad.objects.all().delete()
        load_data_from_sql('catalogos/modalidades.sql')
        
        #Estado.objects.all().delete()
        importar_datos_desde_csv('catalogos/CatalogoInegiEstatal.csv', Estado, {
            'id': 'CVE_ENT',
            'nombre': 'NOM_ENT'
        })
        #Municipio.objects.all().delete()
        importar_datos_desde_csv('catalogos/CatalogoInegiMunicipal.csv', Municipio, {
            'cve_mun': 'CVE_MUN',
            'estado_id': 'CVE_ENT',
            'nombre': 'NOM_MUN'
        })
        
        #Institucion.objects.all().delete()
        importar_datos_desde_csv('catalogos/institutos.csv', Institucion, {
            'id': 'id',
            'nombre': 'instituto',
            'puntos': 'puntos'
        })
        #Carrera.objects.all().delete()
        importar_datos_desde_csv('catalogos/carreras.csv', Carrera, {
            'id': 'id',
            'institucion_id': 'instituto',
            'nombre': 'carrera',
            'puntos': 'puntos'
        })        
        #PuntajeGeneral.objects.all().delete()
        importar_datos_desde_csv('catalogos/PuntajesGeneral.csv', PuntajeGeneral, {
            'id': 'id',
            'tipo': 'tipo',
            'nombre': 'nombre',
            'puntos': 'puntos'
        })                
              
        #Solicitante.objects.all().delete()
        importar_datos_desde_csv('catalogos/SolicitantesReingreso.csv', Solicitante, {
            'id' : 'id',
            'nombre' : 'personalData.name',
            'curp' : 'curp',
            'email' : 'email',
            'password' : 'password',
            'rfc' : 'personalData.rfc',
            'ap_paterno' : 'personalData.fstSurname',
            'ap_materno' : 'personalData.sndSurname',            
            'genero' : 'personalData.gender',
            'g_etnico' : 'personalData.ethnicGroup',
            'colonia' : 'addressData.neighborhood',
            'calle' : 'addressData.street',
            'numero' : 'addressData.number',
            'codigo_postal' : 'addressData.postalCode',
            'tel_cel' : 'addressData.mobilePhoneNumber',
            'tel_fijo' : 'addressData.housePhoneNumber',                        
        }, separador=';')
        
        #Solicitud.objects.all().delete()
        importar_datos_desde_csv('catalogos/SolicitantesReingreso.csv', Solicitud, {
            'id' : 'id',
            'modalidad_id' : 'scholarshipRecord',
            'solicitante_id' : 'id',
            'ciclo' : 'ciclo',
            'estado' : 'estadoSolicitud'
        }, separador=';')

        GenerarNotificacionesUsuarios('Como solicitante aplicable para renovación sel le pide que porfavor revise y actualize su informacion personal en su perfil.', 
                                      'catalogos/SolicitantesReingreso.csv', 'id', separador=';')
        print('\n\n')
        
        break
    elif respuesta in {'n', 'no'}:
        break
    else:        
        print("Respuesta no válida. Por favor, ingresa 'Sí' o 'No'.")



