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

--SHOW TABLE STATUS LIKE 'estudio_socio_economico_seccion';
--SHOW TABLE STATUS LIKE 'estudio_socio_economico_elemento';
--SHOW TABLE STATUS LIKE 'estudio_socio_economico_opcion';
--
-- Dumping data for table `estudio_socio_economico_seccion`
--

LOCK TABLES `estudio_socio_economico_seccion` WRITE;
/*!40000 ALTER TABLE `estudio_socio_economico_seccion` DISABLE KEYS */;
INSERT INTO `estudio_socio_economico_seccion` (id, nombre, tipo, orden) VALUES (43,'Datos Socioeconómicos','unico',2),(44,'Datos familiares (Deben ser todos con los que vives)','agregacion',3);
/*!40000 ALTER TABLE `estudio_socio_economico_seccion` ENABLE KEYS */;
UNLOCK TABLES;
ALTER TABLE `db-becas`.estudio_socio_economico_seccion AUTO_INCREMENT=45;

--
-- Dumping data for table `estudio_socio_economico_elemento`
--

LOCK TABLES `estudio_socio_economico_elemento` WRITE;
/*!40000 ALTER TABLE `estudio_socio_economico_elemento` DISABLE KEYS */;
INSERT INTO `estudio_socio_economico_elemento` (id, nombre, obligatorio, opcionOtro, numMin, numMax, row, col, tipo, seccion_id) VALUES (58,'Ocupación',1,1,0,10,2,1,'texto_corto',43),(59,'Teléfono de trabajo',0,1,10,10,2,2,'numerico',43),(60,'Hora de entrada',0,1,0,10,2,4,'hora',43),(61,'Hora de salida',0,1,0,10,2,5,'hora',43),(62,'Sueldo mensual',0,1,0,10,2,3,'numerico',43),(63,'Actualmente Vives con:',1,0,0,10,6,1,'opcion_multiple',43),(64,'Años viviendo ahí',1,1,0,10,6,2,'numerico',43),(65,'Personas viviendo contigo',1,1,0,10,6,3,'numerico',43),(66,'Vivienda y transporte',1,1,0,10,4,1,'separador',43),(67,'La casa donde vives es:',1,1,0,10,8,1,'opcion_multiple',43),(68,'El material del piso es:',1,1,0,10,8,2,'opcion_multiple',43),(72,'¿Cuántas recámaras tiene?',1,1,0,10,8,3,'numerico',43),(73,'¿Cuántos baños tiene?',1,1,0,10,10,1,'numerico',43),(74,'¿Tiene sala?',1,0,0,10,10,2,'opcion_multiple',43),(75,'¿Tiene cocina independiente?',1,0,0,10,10,3,'opcion_multiple',43),(76,'¿Cuántos autos tiene?',1,1,0,10,10,4,'numerico',43),(77,'¿con que servicios Cuenta?',1,0,0,10,12,1,'casillas',43),(78,'En tu casa cuentas con:',1,0,0,10,14,1,'casillas',43),(79,'¿Cuentas con seguro de gastos Médicos?',1,0,0,10,16,1,'opcion_multiple',43),(80,'¿Qué transporte utilizas?',1,1,0,10,16,2,'opcion_multiple',43),(81,'Nombre completo',1,1,0,10,2,1,'texto_corto',44),(82,'Parentesco',1,1,0,10,2,2,'desplegable',44),(83,'Estado civil',1,0,0,10,2,3,'desplegable',44),(84,'Edad (años)',1,1,0,3,4,1,'numerico',44),(85,'sexo',1,0,0,10,4,2,'opcion_multiple',44),(86,'Escolaridad',1,0,0,10,4,3,'desplegable',44),(87,'¿Termino la carrera?',1,0,0,10,4,4,'opcion_multiple',44),(88,'¿Percibe algún ingreso?',1,0,0,10,6,1,'opcion_multiple',44),(89,'Ocupación',0,0,0,10,6,2,'desplegable',44),(90,'Lugar de Trabajo',0,1,0,10,6,3,'texto_corto',44),(91,'Ingreso mensual',0,1,0,10,6,4,'numerico',44);
/*!40000 ALTER TABLE `estudio_socio_economico_elemento` ENABLE KEYS */;
UNLOCK TABLES;
ALTER TABLE `db-becas`.estudio_socio_economico_elemento AUTO_INCREMENT=92;

--
-- Dumping data for table `estudio_socio_economico_opcion`
--

LOCK TABLES `estudio_socio_economico_opcion` WRITE;
/*!40000 ALTER TABLE `estudio_socio_economico_opcion` DISABLE KEYS */;
INSERT INTO `estudio_socio_economico_opcion` (id, nombre, orden, elemento_id) VALUES (26,'Padres',2,63),(27,'Amigos',4,63),(28,'Familiares',3,63),(29,'Esposo(a)',5,63),(30,'Propia',1,67),(31,'Rentada',2,67),(32,'Casa de huéspedes',3,67),(33,'Tierra',1,68),(34,'Alfombra',2,68),(35,'Madera',3,68),(36,'Duela',4,68),(37,'Cemento',5,68),(39,'Mosaico',6,68),(48,'Si',1,74),(49,'No',2,74),(50,'Si',1,75),(51,'No',2,75),(52,'Agua',1,77),(53,'Luz',2,77),(54,'Drenaje',3,77),(55,'Pavimiento',4,77),(56,'Télefono',5,77),(57,'Gas',6,77),(58,'TV por cable',7,77),(59,'Internet',8,77),(60,'DVD',1,78),(61,'Televisión',2,78),(62,'Estufa',3,78),(63,'Licuadora',4,78),(64,'Lavadora',5,78),(65,'Estéreo',6,78),(66,'Microondas',7,78),(67,'Computadora',8,78),(68,'Si',1,79),(69,'No',2,79),(70,'Auto propio',1,80),(71,'Auto familiar',2,80),(72,'Motocicleta',3,80),(73,'Camión',4,80),(74,'Taxi',5,80),(75,'Caminando',6,80),(76,'Padre',1,82),(77,'Madre',2,82),(78,'Hermano(a)',3,82),(79,'Hijo(a)',4,82),(80,'Abuelo(a)',5,82),(81,'Tío(a)',6,82),(82,'Tutor(a)',7,82),(83,'Esposo(a)',8,82),(84,'Soltero(a)',1,83),(85,'Casado(a)',2,83),(86,'Divorciado(a)',3,83),(87,'Viudo(a)',4,83),(88,'Hombre',1,85),(89,'Mujer',2,85),(90,'Ninguno',1,86),(91,'Primaria',2,86),(92,'Secuandaria',3,86),(93,'Preparatoria',4,86),(94,'Carrera técnica',5,86),(95,'Licenciatura',6,86),(96,'Maestria',7,86),(97,'Posgrado',8,86),(98,'Si',1,87),(99,'No',2,87),(100,'Si',1,88),(101,'No',2,88),(102,'Estudiante',1,89),(103,'Hogar',2,89),(104,'Comerciante',3,89),(105,'Jubilado / Pensionado',4,89),(106,'Obrero',5,89),(107,'Técnico',6,89),(108,'Profesionista',7,89),(109,'Empleado',8,89),(114,'Otro',0,NULL);
/*!40000 ALTER TABLE `estudio_socio_economico_opcion` ENABLE KEYS */;
UNLOCK TABLES;
ALTER TABLE `db-becas`.estudio_socio_economico_opcion AUTO_INCREMENT=115;


