-- MySQL dump 10.13  Distrib 8.1.0, for Win64 (x86_64)
--
-- Host: localhost    Database: db-becas
-- ------------------------------------------------------
-- Server version	5.5.5-10.11.2-MariaDB-1:10.11.2+maria~ubu2204

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Dumping data for table `estudio_socio_economico_elemento`
--
UNLOCK TABLES;
LOCK TABLES `estudio_socio_economico_elemento` WRITE;
/*!40000 ALTER TABLE `estudio_socio_economico_elemento` DISABLE KEYS */;
INSERT INTO `estudio_socio_economico_elemento` VALUES (58,'Ocupación',1,1,'texto_corto',43,2,1,10,0),(59,'Teléfono de trabajo',0,2,'numerico',43,2,1,10,10),(60,'Hora de entrada',0,4,'hora',43,2,1,10,0),(61,'Hora de salida',0,5,'hora',43,2,1,10,0),(62,'Sueldo mensual',0,3,'numerico',43,2,1,10,0),(63,'Actualmente Vives con:',1,1,'opcion_multiple',43,6,0,10,0),(64,'Años viviendo ahí',1,2,'numerico',43,6,1,10,0),(65,'Personas viviendo contigo',1,3,'numerico',43,6,1,10,0),(66,'Vivienda y transporte',1,1,'separador',43,4,1,10,0),(67,'La casa donde vives es:',1,1,'opcion_multiple',43,8,1,10,0),(68,'El material del piso es:',1,2,'opcion_multiple',43,8,1,10,0),(72,'¿Cuántas recámaras tiene?',1,3,'numerico',43,8,1,10,0),(73,'¿Cuántos baños tiene?',1,1,'numerico',43,10,1,10,0),(74,'¿Tiene sala?',1,2,'opcion_multiple',43,10,0,10,0),(75,'¿Tiene cocina independiente?',1,3,'opcion_multiple',43,10,0,10,0),(76,'¿Cuántos autos tiene?',1,4,'numerico',43,10,1,10,0),(77,'¿con que servicios Cuenta?',1,1,'casillas',43,12,0,10,0),(78,'En tu casa cuentas con:',1,1,'casillas',43,14,0,10,0),(79,'¿Cuentas con seguro de gastos Médicos?',1,1,'opcion_multiple',43,16,0,10,0),(80,'¿Qué transporte utilizas?',1,2,'opcion_multiple',43,16,1,10,0),(81,'Nombre completo',1,1,'texto_corto',44,2,1,10,0),(82,'Parentesco',1,2,'desplegable',44,2,1,10,0),(83,'Estado civil',1,3,'desplegable',44,2,0,10,0),(84,'Edad (años)',1,1,'numerico',44,4,1,3,0),(85,'sexo',1,2,'opcion_multiple',44,4,0,10,0),(86,'Escolaridad',1,3,'desplegable',44,4,0,10,0),(87,'¿Termino la carrera?',1,4,'opcion_multiple',44,4,0,10,0),(88,'¿Percibe algún ingreso?',1,1,'opcion_multiple',44,6,0,10,0),(89,'Ocupación',0,2,'desplegable',44,6,0,10,0),(90,'Lugar de Trabajo',0,3,'texto_corto',44,6,1,10,0),(91,'Ingreso mensual',0,4,'numerico',44,6,1,10,0),(125,'pregunta 1',1,1,'texto_corto',48,2,1,10,0),(126,'pregunta 2',1,2,'texto_parrafo',48,2,1,10,0),(127,'pregunta 3',1,3,'numerico',48,2,1,10,0);
/*!40000 ALTER TABLE `estudio_socio_economico_elemento` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `estudio_socio_economico_opcion`
--

LOCK TABLES `estudio_socio_economico_opcion` WRITE;
/*!40000 ALTER TABLE `estudio_socio_economico_opcion` DISABLE KEYS */;
INSERT INTO `estudio_socio_economico_opcion` VALUES (26,'Padres',63,2),(27,'Amigos',63,4),(28,'Familiares',63,3),(29,'Esposo(a)',63,5),(30,'Propia',67,1),(31,'Rentada',67,2),(32,'Casa de huéspedes',67,3),(33,'Tierra',68,1),(34,'Alfombra',68,2),(35,'Madera',68,3),(36,'Duela',68,4),(37,'Cemento',68,5),(39,'Mosaico',68,6),(48,'Si',74,1),(49,'No',74,2),(50,'Si',75,1),(51,'No',75,2),(52,'Agua',77,1),(53,'Luz',77,2),(54,'Drenaje',77,3),(55,'Pavimiento',77,4),(56,'Télefono',77,5),(57,'Gas',77,6),(58,'TV por cable',77,7),(59,'Internet',77,8),(60,'DVD',78,1),(61,'Televisión',78,2),(62,'Estufa',78,3),(63,'Licuadora',78,4),(64,'Lavadora',78,5),(65,'Estéreo',78,6),(66,'Microondas',78,7),(67,'Computadora',78,8),(68,'Si',79,1),(69,'No',79,2),(70,'Auto propio',80,1),(71,'Auto familiar',80,2),(72,'Motocicleta',80,3),(73,'Camión',80,4),(74,'Taxi',80,5),(75,'Caminando',80,6),(76,'Padre',82,1),(77,'Madre',82,2),(78,'Hermano(a)',82,3),(79,'Hijo(a)',82,4),(80,'Abuelo(a)',82,5),(81,'Tío(a)',82,6),(82,'Tutor(a)',82,7),(83,'Esposo(a)',82,8),(84,'Soltero(a)',83,1),(85,'Casado(a)',83,2),(86,'Divorciado(a)',83,3),(87,'Viudo(a)',83,4),(88,'Hombre',85,1),(89,'Mujer',85,2),(90,'Ninguno',86,1),(91,'Primaria',86,2),(92,'Secuandaria',86,3),(93,'Preparatoria',86,4),(94,'Carrera técnica',86,5),(95,'Licenciatura',86,6),(96,'Maestria',86,7),(97,'Posgrado',86,8),(98,'Si',87,1),(99,'No',87,2),(100,'Si',88,1),(101,'No',88,2),(102,'Estudiante',89,1),(103,'Hogar',89,2),(104,'Comerciante',89,3),(105,'Jubilado / Pensionado',89,4),(106,'Obrero',89,5),(107,'Técnico',89,6),(108,'Profesionista',89,7),(109,'Empleado',89,8),(114,'Otro',NULL,0);
/*!40000 ALTER TABLE `estudio_socio_economico_opcion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `estudio_socio_economico_seccion`
--

LOCK TABLES `estudio_socio_economico_seccion` WRITE;
/*!40000 ALTER TABLE `estudio_socio_economico_seccion` DISABLE KEYS */;
INSERT INTO `estudio_socio_economico_seccion` VALUES (43,'Datos Socioeconómicos','unico',2),(44,'Datos familiares (Deben ser todos con los que vives)','agregacion',3),(48,'Prueba 1','agregacion',1);
/*!40000 ALTER TABLE `estudio_socio_economico_seccion` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-11-09 17:13:27
