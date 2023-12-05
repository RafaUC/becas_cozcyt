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

/*SHOW TABLE STATUS LIKE 'estudio_socio_economico_seccion'; */
/*SHOW TABLE STATUS LIKE 'estudio_socio_economico_elemento'; */
/*SHOW TABLE STATUS LIKE 'estudio_socio_economico_opcion'; */
--
-- Dumping data for table `estudio_socio_economico_seccion`
--

LOCK TABLES `estudio_socio_economico_seccion` WRITE;
/*!40000 ALTER TABLE `estudio_socio_economico_seccion` DISABLE KEYS */;
INSERT INTO `estudio_socio_economico_seccion` (id, nombre, tipo, orden) VALUES (1,'Datos Socioeconómicos', 'unico', 2),(2,'Datos familiares (Deben ser todos con los que vives)','agregacion',3);
/*!40000 ALTER TABLE `estudio_socio_economico_seccion` ENABLE KEYS */;
UNLOCK TABLES;
ALTER TABLE `estudio_socio_economico_seccion` AUTO_INCREMENT=3;

--
-- Dumping data for table `estudio_socio_economico_elemento`
--

LOCK TABLES `estudio_socio_economico_elemento` WRITE;
/*!40000 ALTER TABLE `estudio_socio_economico_elemento` DISABLE KEYS */;
INSERT INTO `estudio_socio_economico_elemento` (id,nombre, obligatorio, opcionOtro, numMin, numMax, row, col, tipo, seccion_id) VALUES (1, 'Ocupación', 1,1,0,10, 2,1,'texto_corto',1),(2, 'Teléfono de trabajo', 0,1,10, 10, 2,2,'numerico', 1),(3, 'Hora de entrada', 0,1,0,10, 2,4,'hora', 1),(4, 'Hora de salida',0,1,0,10, 2,5,'hora', 1),(5, 'Sueldo mensual',0,1,0,10, 2,3,'numerico', 1),(32,'Sueldo familiar mensual (Sueldo mensual del cual dependes economicamente)',0,1,0,10, 3,3,'numerico', 1),(6, 'Actualmente Vives con:',1,0,0,10, 6,1,'opcion_multiple',1),(7, 'Años viviendo ahí', 1,1,0,10, 6,2,'numerico', 1),(8, 'Personas viviendo contigo', 1,1,0,10, 6,3,'numerico', 1),(9, 'Vivienda y transporte', 1,1,0,10, 4,1,'separador',1),(10,'La casa donde vives es:', 1,1,0,10, 8,1,'opcion_multiple',1),(11,'El material del piso es:',1,1,0,10, 8,2,'opcion_multiple',1),(12,'¿Cuántas recámaras tiene?', 1,1,0,10, 8,3,'numerico', 1),(13,'¿Cuántos baños tiene?', 1,1,0,10, 10, 1,'numerico', 1),(14,'¿Tiene sala?',1,0,0,10, 10, 2,'opcion_multiple',1),(15,'¿Tiene cocina independiente?',1,0,0,10, 10, 3,'opcion_multiple',1),(16,'¿Cuántos autos tiene?', 1,1,0,10, 10, 4,'numerico', 1),(17,'¿con que servicios Cuenta?',1,0,0,10, 12, 1,'casillas', 1),(18,'En tu casa cuentas con:', 1,0,0,10, 14, 1,'casillas', 1),(19,'¿Cuentas con seguro de gastos Médicos?',1,0,0,10, 16, 1,'opcion_multiple',1),(20,'¿Qué transporte utilizas?', 1,1,0,10, 16, 2,'opcion_multiple',1),(21,'Nombre completo', 1,1,0,10, 2,1,'texto_corto',2),(22,'Parentesco',1,1,0,10, 2,2,'desplegable',2),(23,'Estado civil',1,0,0,10, 2,3,'desplegable',2),(24,'Edad (años)', 1,1,0,3,4,1,'numerico', 2),(25,'sexo',1,0,0,10, 4,2,'opcion_multiple',2),(26,'Escolaridad', 1,0,0,10, 4,3,'desplegable',2),(27,'¿Termino la carrera?',1,0,0,10, 4,4,'opcion_multiple',2),(28,'¿Percibe algún ingreso?', 1,0,0,10, 6,1,'opcion_multiple',2),(29,'Ocupación', 0,0,0,10, 6,2,'desplegable',2),(30,'Lugar de Trabajo',0,1,0,10, 6,3,'texto_corto',2),(31,'Ingreso mensual', 0,1,0,10, 6,4,'numerico', 2);
/*!40000 ALTER TABLE `estudio_socio_economico_elemento` ENABLE KEYS */;
UNLOCK TABLES;
ALTER TABLE `estudio_socio_economico_elemento` AUTO_INCREMENT=33;

--
-- Dumping data for table `estudio_socio_economico_opcion`
--

LOCK TABLES `estudio_socio_economico_opcion` WRITE;
/*!40000 ALTER TABLE `estudio_socio_economico_opcion` DISABLE KEYS */;
INSERT INTO `estudio_socio_economico_opcion` (id, nombre,orden, elemento_id) VALUES (1, 'Otro', 0,NULL),(2, 'Padres', 2,6),(3, 'Amigos', 4,6),(4, 'Familiares', 3,6),(5, 'Esposo(a)',5,6),(6, 'Propia', 1,10),(7, 'Rentada',2,10),(8, 'Casa de huéspedes',3,10),(9, 'Tierra', 1,11),(10,'Alfombra', 2,11),(11,'Madera', 3,11),(12,'Duela',4,11),(13,'Cemento',5,11),(14,'Mosaico',6,11),(15,'Si', 1,14),(16,'No', 2,14),(17,'Si', 1,15),(18,'No', 2,15),(19,'Agua', 1,17),(20,'Luz',2,17),(21,'Drenaje',3,17),(22,'Pavimiento', 4,17),(23,'Télefono', 5,17),(24,'Gas',6,17),(25,'TV por cable', 7,17),(26,'Internet', 8,17),(27,'DVD',1,18),(28,'Televisión', 2,18),(29,'Estufa', 3,18),(30,'Licuadora',4,18),(31,'Lavadora', 5,18),(32,'Estéreo',6,18),(33,'Microondas', 7,18),(34,'Computadora',8,18),(35,'Si', 1,19),(36,'No', 2,19),(37,'Auto propio',1,20),(38,'Auto familiar',2,20),(39,'Motocicleta',3,20),(40,'Camión', 4,20),(41,'Taxi', 5,20),(42,'Caminando',6,20),(43,'Padre',1,22),(44,'Madre',2,22),(45,'Hermano(a)', 3,22),(46,'Hijo(a)',4,22),(47,'Abuelo(a)',5,22),(48,'Tío(a)', 6,22),(49,'Tutor(a)', 7,22),(50,'Esposo(a)',8,22),(51,'Soltero(a)', 1,23),(52,'Casado(a)',2,23),(53,'Divorciado(a)',3,23),(54,'Viudo(a)', 4,23),(55,'Hombre', 1,25),(56,'Mujer',2,25),(57,'Ninguno',1,26),(58,'Primaria', 2,26),(59,'Secuandaria',3,26),(60,'Preparatoria', 4,26),(61,'Carrera técnica',5,26),(62,'Licenciatura', 6,26),(63,'Maestria', 7,26),(64,'Posgrado', 8,26),(65,'Si', 1,27),(66,'No', 2,27),(67, 'Si',1,28),(68, 'No',2,28),(69, 'Estudiante',1,29),(70, 'Hogar', 2,29),(71, 'Comerciante', 3,29),(72, 'Jubilado / Pensionado', 4,29),(73, 'Obrero',5,29),(74, 'Técnico', 6,29),(75, 'Profesionista', 7,29),(76, 'Empleado',8,29);
/*!40000 ALTER TABLE `estudio_socio_economico_opcion` ENABLE KEYS */;
UNLOCK TABLES;
ALTER TABLE `estudio_socio_economico_opcion` AUTO_INCREMENT=77;
