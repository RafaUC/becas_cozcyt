
INSERT INTO `usuarios_institucion` (`id`, `nombre`, `puntos`, `created_at`, `updated_at`) VALUES
(2, 'BENMAC2', 6, '2022-07-18 10:37:43', '2022-11-05 09:17:48'),
(3, 'UTZAC', 89, '2022-08-06 01:50:16', '2022-11-05 09:17:59');

INSERT INTO `usuarios_carrera` (`id`, `nombre`, `puntos`, `institucion_id`, `created_at`, `updated_at`, `deleted_at`) VALUES
(1, 'Tecnologías de la información', 5, 2, '2022-08-06 01:50:59', '2022-10-31 21:26:06', NULL),
(4, 'Ing Tecnologías de la información', 5, 3, '2022-10-31 21:24:44', '2022-10-31 21:24:58', NULL);

INSERT INTO `usuarios_estado` (`id`, `nombre`, `created_at`, `updated_at`) VALUES
(1, 'Zacatecas', '2022-10-10 03:12:49', NULL);

INSERT INTO `usuarios_municipio` (`id`, `nombre`, `estado_id`, `created_at`, `updated_at`) VALUES
(1, 'Guadalupe', 1, '2022-10-10 03:13:18', NULL),
(2, 'Villa de cos', 1, '2022-10-10 03:13:32', NULL);