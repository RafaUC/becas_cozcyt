import os
import django
from django.db import migrations, models, connection
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'becas_cozcyt.settings')
django.setup()

def load_data_from_sql(sqlFile):
   file_path = os.path.join(os.path.dirname(__file__), sqlFile)
   sql_statement = open(file_path).read()
   print(sql_statement)
   with connection.cursor() as c:
       c.execute(sql_statement)

load_data_from_sql('estudioSE.sql')
load_data_from_sql('catalogos.sql')

""""
class Migration(migrations.Migration):
    dependencies = [
        ('..', '...'),
    ]

    operations = [
        migrations.RunPython(load_data_from_sql),
    ]
    """