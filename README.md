# becas_cozcyt
PASOS:
- docker compose up --build

una vez completado, ejecutar:
- docker exec -it sistema_becas /bin/bash
- python3 manage.py makemigrations
- python3 manage.py migrate
- python3 gruposYPermisos.py
- python3 generarCatalogos.py
