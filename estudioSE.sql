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

LOCK TABLES `estudio_socio_economico_elemento` WRITE;
/*!40000 ALTER TABLE `estudio_socio_economico_elemento` DISABLE KEYS */;
INSERT INTO `estudio_socio_economico_elemento` VALUES (58,'Ocupación',1,1,'texto_corto',43,2,1,10,0),(59,'Teléfono de trabajo',0,2,'numerico',43,2,1,10,10),(60,'Hora de entrada',0,4,'hora',43,2,1,10,0),(61,'Hora de salida',0,5,'hora',43,2,1,10,0),(62,'Sueldo mensual',0,3,'numerico',43,2,1,10,0),(63,'Actualmente Vives con:',1,1,'opcion_multiple',43,6,0,10,0),(64,'Años viviendo ahí',1,2,'numerico',43,6,1,10,0),(65,'Personas viviendo contigo',1,3,'numerico',43,6,1,10,0),(66,'Vivienda y transporte',1,1,'separador',43,4,1,10,0),(67,'La casa donde vives es:',1,1,'opcion_multiple',43,8,1,10,0),(68,'El material del piso es:',1,2,'opcion_multiple',43,8,1,10,0),(72,'¿Cuántas recámaras tiene?',1,3,'numerico',43,8,1,10,0),(73,'¿Cuántos baños tiene?',1,1,'numerico',43,10,1,10,0),(74,'¿Tiene sala?',1,2,'opcion_multiple',43,10,0,10,0),(75,'¿Tiene cocina independiente?',1,3,'opcion_multiple',43,10,0,10,0),(76,'¿Cuántos autos tiene?',1,4,'numerico',43,10,1,10,0),(77,'¿con que servicios Cuenta?',1,1,'casillas',43,12,0,10,0),(78,'En tu casa cuentas con:',1,1,'casillas',43,14,0,10,0),(79,'¿Cuentas con seguro de gastos Médicos?',1,1,'opcion_multiple',43,16,0,10,0),(80,'¿Qué transporte utilizas?',1,2,'opcion_multiple',43,16,1,10,0),(81,'Nombre completo',1,1,'texto_corto',44,2,1,10,0),(82,'Parentesco',1,2,'desplegable',44,2,1,10,0),(83,'Estado civil',1,3,'desplegable',44,2,0,10,0),(84,'Edad (años)',1,1,'numerico',44,4,1,3,0),(85,'sexo',1,2,'opcion_multiple',44,4,0,10,0),(86,'Escolaridad',1,3,'desplegable',44,4,0,10,0),(87,'¿Termino la carrera?',1,4,'opcion_multiple',44,4,0,10,0),(88,'¿Percibe algún ingreso?',1,1,'opcion_multiple',44,6,0,10,0),(89,'Ocupación',0,2,'desplegable',44,6,0,10,0),(90,'Lugar de Trabajo',0,3,'texto_corto',44,6,1,10,0),(91,'Ingreso mensual',0,4,'numerico',44,6,1,10,0);
/*!40000 ALTER TABLE `estudio_socio_economico_elemento` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `estudio_socio_economico_mymodel`
--

LOCK TABLES `estudio_socio_economico_mymodel` WRITE;
/*!40000 ALTER TABLE `estudio_socio_economico_mymodel` DISABLE KEYS */;
/*!40000 ALTER TABLE `estudio_socio_economico_mymodel` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `estudio_socio_economico_opcion`
--

LOCK TABLES `estudio_socio_economico_opcion` WRITE;
/*!40000 ALTER TABLE `estudio_socio_economico_opcion` DISABLE KEYS */;
INSERT INTO `estudio_socio_economico_opcion` VALUES (26,'Padres',63,2),(27,'Amigos',63,4),(28,'Familiares',63,3),(29,'Esposo(a)',63,5),(30,'Propia',67,100000),(31,'Rentada',67,100000),(32,'Casa de huéspedes',67,100000),(33,'Tierra',68,100000),(34,'Alfombra',68,100000),(35,'Madera',68,100000),(36,'Duela',68,100000),(37,'Cemento',68,100000),(39,'Mosaico',68,100000),(48,'Si',74,100000),(49,'No',74,100000),(50,'Si',75,100000),(51,'No',75,100000),(52,'Agua',77,100000),(53,'Luz',77,100000),(54,'Drenaje',77,100000),(55,'Pavimiento',77,100000),(56,'Télefono',77,100000),(57,'Gas',77,100000),(58,'TV por cable',77,100000),(59,'Internet',77,100000),(60,'DVD',78,100000),(61,'Televisión',78,100000),(62,'Estufa',78,100000),(63,'Licuadora',78,100000),(64,'Lavadora',78,100000),(65,'Estéreo',78,100000),(66,'Microondas',78,100000),(67,'Computadora',78,100000),(68,'Si',79,100000),(69,'No',79,100000),(70,'Auto propio',80,100000),(71,'Auto familiar',80,100000),(72,'Motocicleta',80,100000),(73,'Camión',80,100000),(74,'Taxi',80,100000),(75,'Caminando',80,100000),(76,'Padre',82,100000),(77,'Madre',82,100000),(78,'Hermano(a)',82,100000),(79,'Hijo(a)',82,100000),(80,'Abuelo(a)',82,100000),(81,'Tío(a)',82,100000),(82,'Tutor(a)',82,100000),(83,'Esposo(a)',82,100000),(84,'Soltero(a)',83,100000),(85,'Casado(a)',83,100000),(86,'Divorciado(a)',83,100000),(87,'Viudo(a)',83,100000),(88,'Hombre',85,100000),(89,'Mujer',85,100000),(90,'Ninguno',86,100000),(91,'Primaria',86,100000),(92,'Secuandaria',86,100000),(93,'Preparatoria',86,100000),(94,'Carrera técnica',86,100000),(95,'Licenciatura',86,100000),(96,'Maestria',86,100000),(97,'Posgrado',86,100000),(98,'Si',87,100000),(99,'No',87,100000),(100,'Si',88,100000),(101,'No',88,100000),(102,'Estudiante',89,100000),(103,'Hogar',89,100000),(104,'Comerciante',89,100000),(105,'Jubilado / Pensionado',89,100000),(106,'Obrero',89,100000),(107,'Técnico',89,100000),(108,'Profesionista',89,100000),(109,'Empleado',89,100000);
/*!40000 ALTER TABLE `estudio_socio_economico_opcion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `estudio_socio_economico_seccion`
--

LOCK TABLES `estudio_socio_economico_seccion` WRITE;
/*!40000 ALTER TABLE `estudio_socio_economico_seccion` DISABLE KEYS */;
INSERT INTO `estudio_socio_economico_seccion` VALUES (43,'Datos Socioeconómicos','único',2),(44,'Datos familiares (Deben ser todos con los que vives)','agregación',100000);
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

-- Dump completed on 2023-08-27 20:34:27
