CREATE TABLE `Usuarios` (
  `id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
  `nombre` VARCHAR(255),
  `email` VARCHAR(255),
  `contraseña` VARCHAR(255),
  `foto_perfil` VARCHAR(255),
  `descripcion` TEXT(65535),
  PRIMARY KEY(`id`)
);

CREATE TABLE `Recetas` (
  `id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
  `id_usuario` INTEGER,
  `titulo` VARCHAR(255),
  `descripcion` TEXT(65535),
  `imagen_portada` VARCHAR(255),
  `tiempor_pre` VARCHAR(255),
  `fecha_creacion` DATETIME,
  PRIMARY KEY(`id`)
);

CREATE TABLE `Instrucciones` (
  `id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
  `id_receta` INTEGER,
  `numero_paso` INTEGER,
  `descripcion` TEXT(65535),
  PRIMARY KEY(`id`)
);

CREATE TABLE `categorias` (
  `id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
  `nombre` VARCHAR(255),
  `descripcion` TEXT(65535),
  PRIMARY KEY(`id`)
);

CREATE TABLE `Receta_categorias` (
  `id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
  `receta_id` INTEGER,
  `categoria_id` INTEGER,
  PRIMARY KEY(`id`)
);

CREATE TABLE `Ingredientes` (
  `id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
  `nombre` VARCHAR(255),
  `unidad_medida` VARCHAR(255),
  PRIMARY KEY(`id`)
);

CREATE TABLE `Receta_ingredientes` (
  `id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
  `receta_id` INTEGER,
  `ingredientes_id` INTEGER,
  `cantidad` INTEGER,
  PRIMARY KEY(`id`)
);

CREATE TABLE `Me_gusta` (
  `id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
  `ususario_id` INTEGER,
  `receta_id` INTEGER,
  PRIMARY KEY(`id`)
);

CREATE TABLE `seguidores` (
  `id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
  `usuario_id` INTEGER,
  `seguidor_id` INTEGER,
  PRIMARY KEY(`id`)
);

ALTER TABLE `Receta_categorias` ADD FOREIGN KEY(`receta_id`) REFERENCES `Recetas`(`id`) ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `Receta_categorias` ADD FOREIGN KEY(`categoria_id`) REFERENCES `categorias`(`id`) ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `Receta_ingredientes` ADD FOREIGN KEY(`receta_id`) REFERENCES `Recetas`(`id`) ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `Receta_ingredientes` ADD FOREIGN KEY(`ingredientes_id`) REFERENCES `Ingredientes`(`id`) ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `Instrucciones` ADD FOREIGN KEY(`id_receta`) REFERENCES `Recetas`(`id`) ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `Recetas` ADD FOREIGN KEY(`id_usuario`) REFERENCES `Usuarios`(`id`) ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `Me_gusta` ADD FOREIGN KEY(`ususario_id`) REFERENCES `Usuarios`(`id`) ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `Me_gusta` ADD FOREIGN KEY(`receta_id`) REFERENCES `Recetas`(`id`) ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `seguidores` ADD FOREIGN KEY(`usuario_id`) REFERENCES `Usuarios`(`id`) ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `seguidores` ADD FOREIGN KEY(`seguidor_id`) REFERENCES `Usuarios`(`id`) ON UPDATE NO ACTION ON DELETE NO ACTION;

-- Insertar algunas categorías de ejemplo
INSERT INTO `categorias` (`nombre`, `descripcion`) VALUES 
('Desayuno', 'Recetas para comenzar el día con energía'),
('Almuerzo', 'Deliciosas comidas para el medio día'),
('Cena', 'Platos ligeros para la noche'),
('Postres', 'Dulces para complementar cualquier comida'),
('Vegano', 'Recetas sin productos de origen animal'),
('Saludable', 'Comidas bajas en calorías'),
('Rápido', 'Recetas que se preparan en menos de 30 minutos');

-- Insertar algunas unidades de medida comunes para ingredientes
INSERT INTO `Ingredientes` (`nombre`, `unidad_medida`) VALUES 
('Harina', 'gramos'),
('Azúcar', 'gramos'),
('Huevos', 'unidad'),
('Leche', 'ml'),
('Aceite de oliva', 'ml'),
('Sal', 'gramos'),
('Pimienta', 'gramos'),
('Ajo', 'dientes'),
('Cebolla', 'unidad'),
('Tomate', 'unidad');