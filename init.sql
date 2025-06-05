-- Limpiar tablas si existen (en orden correcto para evitar errores de FK)
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `seguidores`;
DROP TABLE IF EXISTS `Me_gusta`;
DROP TABLE IF EXISTS `Receta_ingredientes`;
DROP TABLE IF EXISTS `Receta_categorias`;
DROP TABLE IF EXISTS `Instrucciones`;
DROP TABLE IF EXISTS `Recetas`;
DROP TABLE IF EXISTS `Ingredientes`;
DROP TABLE IF EXISTS `categorias`;
DROP TABLE IF EXISTS `Usuarios`;
SET FOREIGN_KEY_CHECKS = 1;

-- Crear tablas
CREATE TABLE `Usuarios` (
  `id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
  `nombre` VARCHAR(255),
  `email` VARCHAR(255),
  `contrasena` VARCHAR(255),
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

-- Agregar claves foráneas
ALTER TABLE `Receta_categorias` ADD FOREIGN KEY(`receta_id`) REFERENCES `Recetas`(`id`) ON UPDATE NO ACTION ON DELETE CASCADE;
ALTER TABLE `Receta_categorias` ADD FOREIGN KEY(`categoria_id`) REFERENCES `categorias`(`id`) ON UPDATE NO ACTION ON DELETE CASCADE;
ALTER TABLE `Receta_ingredientes` ADD FOREIGN KEY(`receta_id`) REFERENCES `Recetas`(`id`) ON UPDATE NO ACTION ON DELETE CASCADE;
ALTER TABLE `Receta_ingredientes` ADD FOREIGN KEY(`ingredientes_id`) REFERENCES `Ingredientes`(`id`) ON UPDATE NO ACTION ON DELETE CASCADE;
ALTER TABLE `Instrucciones` ADD FOREIGN KEY(`id_receta`) REFERENCES `Recetas`(`id`) ON UPDATE NO ACTION ON DELETE CASCADE;
ALTER TABLE `Recetas` ADD FOREIGN KEY(`id_usuario`) REFERENCES `Usuarios`(`id`) ON UPDATE NO ACTION ON DELETE CASCADE;
ALTER TABLE `Me_gusta` ADD FOREIGN KEY(`ususario_id`) REFERENCES `Usuarios`(`id`) ON UPDATE NO ACTION ON DELETE CASCADE;
ALTER TABLE `Me_gusta` ADD FOREIGN KEY(`receta_id`) REFERENCES `Recetas`(`id`) ON UPDATE NO ACTION ON DELETE CASCADE;
ALTER TABLE `seguidores` ADD FOREIGN KEY(`usuario_id`) REFERENCES `Usuarios`(`id`) ON UPDATE NO ACTION ON DELETE CASCADE;
ALTER TABLE `seguidores` ADD FOREIGN KEY(`seguidor_id`) REFERENCES `Usuarios`(`id`) ON UPDATE NO ACTION ON DELETE CASCADE;

-- ===========================================
-- DATOS DE PRUEBA
-- ===========================================

-- 1. INSERTAR CATEGORÍAS
INSERT INTO `categorias` (`nombre`, `descripcion`) VALUES 
('Desayuno', 'Recetas para comenzar el día con energía'),
('Almuerzo', 'Deliciosas comidas para el medio día'),
('Cena', 'Platos ligeros para la noche'),
('Postres', 'Dulces para complementar cualquier comida'),
('Vegano', 'Recetas sin productos de origen animal'),
('Saludable', 'Comidas bajas en calorías'),
('Rápido', 'Recetas que se preparan en menos de 30 minutos'),
('Italiano', 'Auténtica cocina italiana'),
('Mexicano', 'Sabores tradicionales mexicanos'),
('Asiático', 'Cocina del continente asiático');

-- 2. INSERTAR INGREDIENTES AMPLIADOS
INSERT INTO `Ingredientes` (`nombre`, `unidad_medida`) VALUES 
-- Básicos
('Harina', 'gramos'),
('Azúcar', 'gramos'),
('Huevos', 'unidad'),
('Leche', 'ml'),
('Aceite de oliva', 'ml'),
('Sal', 'gramos'),
('Pimienta', 'gramos'),
('Ajo', 'dientes'),
('Cebolla', 'unidad'),
('Tomate', 'unidad'),
-- Proteínas
('Pollo', 'gramos'),
('Carne de res', 'gramos'),
('Pescado', 'gramos'),
('Queso mozzarella', 'gramos'),
('Queso parmesano', 'gramos'),
-- Vegetales
('Pimientos', 'unidad'),
('Zanahoria', 'unidad'),
('Apio', 'tallos'),
('Espinaca', 'gramos'),
('Brócoli', 'gramos'),
-- Condimentos y especias
('Orégano', 'cucharaditas'),
('Albahaca', 'gramos'),
('Comino', 'cucharaditas'),
('Paprika', 'cucharaditas'),
('Cilantro', 'gramos'),
-- Carbohidratos
('Pasta', 'gramos'),
('Arroz', 'gramos'),
('Pan', 'rebanadas'),
('Tortillas', 'unidad'),
('Avena', 'gramos'),
-- Lácteos y otros
('Mantequilla', 'gramos'),
('Crema', 'ml'),
('Yogur', 'gramos'),
('Limón', 'unidad'),
('Aguacate', 'unidad'),
-- Para postres
('Chocolate', 'gramos'),
('Vainilla', 'cucharaditas'),
('Canela', 'cucharaditas'),
('Fresas', 'gramos'),
('Plátano', 'unidad');

-- 3. INSERTAR USUARIOS (con contraseñas hasheadas - password123 para todos)
INSERT INTO `Usuarios` (`nombre`, `email`, `contrasena`, `foto_perfil`, `descripcion`) VALUES 
('María González', 'maria.gonzalez@gmail.com', 'pbkdf2:sha256:600000$7j8Xn9Kq$8f5e2a1d9c7b6e4f3a0d8c7b6e5f4a3d2c1b0a9e8d7c6b5a4f3e2d1c0b9a8e7d', 'uploads/perfiles/maria.jpg', 'Chef profesional especializada en cocina mediterránea. Me encanta compartir recetas familiares que han pasado de generación en generación.'),
('Carlos Rodríguez', 'carlos.rodriguez@gmail.com', 'pbkdf2:sha256:600000$8k9Yo0Lr$9g6f3b2e0d9c8b7a6f5e4d3c2b1a0f9e8d7c6b5a4f3e2d1c0b9a8e7d6c5b4a3f', 'uploads/perfiles/carlos.jpg', 'Estudiante de gastronomía apasionado por la cocina rápida y saludable. Siempre experimento con nuevos sabores y técnicas culinarias.'),
('Ana Martínez', 'ana.martinez@gmail.com', 'pbkdf2:sha256:600000$9l0Zp1Ms$0h7g4c3f1e0d9c8b7a6f5e4d3c2b1a0f9e8d7c6b5a4f3e2d1c0b9a8e7d6c5b4a', 'uploads/perfiles/ana.jpg', 'Nutricionista especializada en comida vegana y saludable. Creo que comer bien no significa sacrificar el sabor. ¡Cocinar es mi terapia!');

-- 4. INSERTAR RECETAS
-- RECETAS DE MARÍA (Usuario 1)
INSERT INTO `Recetas` (`id_usuario`, `titulo`, `descripcion`, `imagen_portada`, `tiempor_pre`, `fecha_creacion`) VALUES 
(1, 'Pasta Carbonara Auténtica', 'La receta tradicional italiana de pasta carbonara, cremosa y deliciosa, con ingredientes simples pero de calidad.', 'uploads/recetas/carbonara.jpg', '20 minutos', '2024-12-01 10:30:00'),
(1, 'Paella Valenciana Tradicional', 'Auténtica paella valenciana con pollo, conejo, judías y azafrán. Una receta familiar de Valencia que ha pasado por generaciones.', 'uploads/recetas/paella.jpg', '45 minutos', '2024-12-05 14:20:00'),
(1, 'Gazpacho Andaluz', 'Refrescante sopa fría perfecta para los días calurosos de verano. Hecha con tomates maduros y vegetales frescos.', 'uploads/recetas/gazpacho.jpg', '15 minutos', '2024-12-10 09:15:00'),
(1, 'Risotto de Champiñones', 'Cremoso risotto italiano con champiñones frescos y queso parmesano. Perfecto para una cena elegante.', 'uploads/recetas/risotto.jpg', '35 minutos', '2024-12-15 19:45:00'),
(1, 'Tiramisu Casero', 'El postre italiano más famoso del mundo. Capas de café, mascarpone y cacao que se derriten en tu boca.', 'uploads/recetas/tiramisu.jpg', '30 minutos + 4 horas refrigeración', '2024-12-20 16:30:00');

-- RECETAS DE CARLOS (Usuario 2)
INSERT INTO `Recetas` (`id_usuario`, `titulo`, `descripcion`, `imagen_portada`, `tiempor_pre`, `fecha_creacion`) VALUES 
(2, 'Tacos de Pollo Marinado', 'Tacos mexicanos con pollo marinado en especias, servidos con guacamole fresco y salsa picante casera.', 'uploads/recetas/tacos_pollo.jpg', '25 minutos', '2024-12-02 12:00:00'),
(2, 'Bowl de Quinoa Saludable', 'Bowl nutritivo con quinoa, vegetales asados, aguacate y aderezo de tahini. Perfecto para un almuerzo ligero.', 'uploads/recetas/quinoa_bowl.jpg', '30 minutos', '2024-12-07 13:45:00'),
(2, 'Stir Fry de Vegetales', 'Salteado asiático rápido con vegetales crujientes y salsa teriyaki casera. Listo en 15 minutos.', 'uploads/recetas/stir_fry.jpg', '15 minutos', '2024-12-12 18:30:00'),
(2, 'Smoothie Bowl de Frutas', 'Desayuno colorido y nutritivo con frutas tropicales, granola casera y semillas de chía.', 'uploads/recetas/smoothie_bowl.jpg', '10 minutos', '2024-12-17 08:20:00'),
(2, 'Pollo Teriyaki', 'Pollo jugoso glaseado con salsa teriyaki casera, servido con arroz jazmín y vegetales al vapor.', 'uploads/recetas/pollo_teriyaki.jpg', '25 minutos', '2024-12-22 20:10:00');

-- RECETAS DE ANA (Usuario 3)
INSERT INTO `Recetas` (`id_usuario`, `titulo`, `descripcion`, `imagen_portada`, `tiempor_pre`, `fecha_creacion`) VALUES 
(3, 'Curry de Lentejas Vegano', 'Curry aromático y reconfortante con lentejas rojas, leche de coco y especias. Rico en proteínas vegetales.', 'uploads/recetas/curry_lentejas.jpg', '30 minutos', '2024-12-03 17:25:00'),
(3, 'Avena Overnight con Frutos Rojos', 'Desayuno saludable que se prepara la noche anterior. Cremoso, nutritivo y lleno de sabor.', 'uploads/recetas/overnight_oats.jpg', '5 minutos + toda la noche', '2024-12-08 07:30:00'),
(3, 'Ensalada de Garbanzos Mediterránea', 'Ensalada fresca y proteica con garbanzos, vegetales mediterráneos y aderezo de hierbas.', 'uploads/recetas/ensalada_garbanzos.jpg', '15 minutos', '2024-12-13 12:40:00'),
(3, 'Hamburguesa Vegana de Frijoles', 'Hamburguesa casera plant-based con frijoles negros, quinoa y especias. Deliciosa y nutritiva.', 'uploads/recetas/burger_vegana.jpg', '35 minutos', '2024-12-18 19:20:00'),
(3, 'Brownie de Chocolate Vegano', 'Brownie húmedo y chocolatoso sin ingredientes de origen animal. Imposible distinguirlo del tradicional.', 'uploads/recetas/brownie_vegano.jpg', '40 minutos', '2024-12-23 15:50:00');

-- 5. ASIGNAR CATEGORÍAS A RECETAS
INSERT INTO `Receta_categorias` (`receta_id`, `categoria_id`) VALUES 
-- Recetas de María
(1, 2), (1, 8), -- Carbonara: Almuerzo, Italiano
(2, 2), (2, 8), -- Paella: Almuerzo, Italiano (Valencia)
(3, 6), (3, 7), -- Gazpacho: Saludable, Rápido
(4, 3), (4, 8), -- Risotto: Cena, Italiano
(5, 4), (5, 8), -- Tiramisu: Postres, Italiano

-- Recetas de Carlos
(6, 2), (6, 9), (6, 7), -- Tacos: Almuerzo, Mexicano, Rápido
(7, 2), (7, 6), (7, 7), -- Quinoa Bowl: Almuerzo, Saludable, Rápido
(8, 3), (8, 10), (8, 7), -- Stir Fry: Cena, Asiático, Rápido
(9, 1), (9, 6), (9, 7), -- Smoothie Bowl: Desayuno, Saludable, Rápido
(10, 3), (10, 10), -- Pollo Teriyaki: Cena, Asiático

-- Recetas de Ana
(11, 2), (11, 5), (11, 6), -- Curry Lentejas: Almuerzo, Vegano, Saludable
(12, 1), (12, 5), (12, 6), -- Overnight Oats: Desayuno, Vegano, Saludable
(13, 2), (13, 5), (13, 6), (13, 7), -- Ensalada Garbanzos: Almuerzo, Vegano, Saludable, Rápido
(14, 3), (14, 5), (14, 6), -- Burger Vegana: Cena, Vegano, Saludable
(15, 4), (15, 5); -- Brownie Vegano: Postres, Vegano

-- 6. ASIGNAR INGREDIENTES A RECETAS
-- Carbonara (Receta 1)
INSERT INTO `Receta_ingredientes` (`receta_id`, `ingredientes_id`, `cantidad`) VALUES 
(1, 26, 400), -- Pasta
(1, 3, 4), -- Huevos
(1, 15, 100), -- Queso parmesano
(1, 8, 3), -- Ajo
(1, 7, 5); -- Pimienta

-- Paella (Receta 2)
INSERT INTO `Receta_ingredientes` (`receta_id`, `ingredientes_id`, `cantidad`) VALUES 
(2, 27, 300), -- Arroz
(2, 11, 500), -- Pollo
(2, 10, 2), -- Tomate
(2, 5, 50), -- Aceite de oliva
(2, 6, 10); -- Sal

-- Gazpacho (Receta 3)
INSERT INTO `Receta_ingredientes` (`receta_id`, `ingredientes_id`, `cantidad`) VALUES 
(3, 10, 6), -- Tomate
(3, 9, 1), -- Cebolla
(3, 8, 2), -- Ajo
(3, 5, 30), -- Aceite de oliva
(3, 33, 1); -- Limón

-- Risotto (Receta 4)
INSERT INTO `Receta_ingredientes` (`receta_id`, `ingredientes_id`, `cantidad`) VALUES 
(4, 27, 300), -- Arroz
(4, 15, 80), -- Queso parmesano
(4, 9, 1), -- Cebolla
(4, 31, 50); -- Mantequilla

-- Tiramisu (Receta 5)
INSERT INTO `Receta_ingredientes` (`receta_id`, `ingredientes_id`, `cantidad`) VALUES 
(5, 3, 6), -- Huevos
(5, 2, 100), -- Azúcar
(5, 36, 200), -- Chocolate
(5, 37, 5); -- Vainilla

-- Tacos de Pollo (Receta 6)
INSERT INTO `Receta_ingredientes` (`receta_id`, `ingredientes_id`, `cantidad`) VALUES 
(6, 11, 400), -- Pollo
(6, 29, 8), -- Tortillas
(6, 34, 2), -- Aguacate
(6, 25, 10), -- Cilantro
(6, 33, 2); -- Limón

-- Quinoa Bowl (Receta 7)
INSERT INTO `Receta_ingredientes` (`receta_id`, `ingredientes_id`, `cantidad`) VALUES 
(7, 27, 150), -- Arroz (sustituyendo quinoa)
(7, 17, 2), -- Zanahoria
(7, 20, 200), -- Brócoli
(7, 34, 1), -- Aguacate
(7, 33, 1); -- Limón

-- Stir Fry (Receta 8)
INSERT INTO `Receta_ingredientes` (`receta_id`, `ingredientes_id`, `cantidad`) VALUES 
(8, 16, 2), -- Pimientos
(8, 17, 2), -- Zanahoria
(8, 20, 200), -- Brócoli
(8, 8, 3), -- Ajo
(8, 5, 30); -- Aceite de oliva

-- Smoothie Bowl (Receta 9)
INSERT INTO `Receta_ingredientes` (`receta_id`, `ingredientes_id`, `cantidad`) VALUES 
(9, 39, 2), -- Plátano
(9, 38, 150), -- Fresas
(9, 30, 50), -- Avena
(9, 33, 250); -- Yogur (sustituyendo)

-- Pollo Teriyaki (Receta 10)
INSERT INTO `Receta_ingredientes` (`receta_id`, `ingredientes_id`, `cantidad`) VALUES 
(10, 11, 500), -- Pollo
(10, 27, 200), -- Arroz
(10, 8, 2), -- Ajo
(10, 2, 30); -- Azúcar

-- Curry de Lentejas (Receta 11)
INSERT INTO `Receta_ingredientes` (`receta_id`, `ingredientes_id`, `cantidad`) VALUES 
(11, 9, 1), -- Cebolla
(11, 8, 3), -- Ajo
(11, 23, 10), -- Comino
(11, 32, 400); -- Crema (sustituyendo leche de coco)

-- Overnight Oats (Receta 12)
INSERT INTO `Receta_ingredientes` (`receta_id`, `ingredientes_id`, `cantidad`) VALUES 
(12, 30, 80), -- Avena
(12, 4, 200), -- Leche
(12, 38, 100), -- Fresas
(12, 2, 20); -- Azúcar

-- Ensalada de Garbanzos (Receta 13)
INSERT INTO `Receta_ingredientes` (`receta_id`, `ingredientes_id`, `cantidad`) VALUES 
(13, 10, 2), -- Tomate
(13, 9, 1), -- Cebolla
(13, 5, 40), -- Aceite de oliva
(13, 33, 1); -- Limón

-- Burger Vegana (Receta 14)
INSERT INTO `Receta_ingredientes` (`receta_id`, `ingredientes_id`, `cantidad`) VALUES 
(14, 28, 4), -- Pan
(14, 9, 1), -- Cebolla
(14, 8, 2), -- Ajo
(14, 30, 50); -- Avena

-- Brownie Vegano (Receta 15)
INSERT INTO `Receta_ingredientes` (`receta_id`, `ingredientes_id`, `cantidad`) VALUES 
(15, 1, 200), -- Harina
(15, 36, 150), -- Chocolate
(15, 2, 150), -- Azúcar
(15, 5, 60); -- Aceite de oliva

-- 7. INSERTAR INSTRUCCIONES PARA TODAS LAS RECETAS
-- Carbonara (Receta 1)
INSERT INTO `Instrucciones` (`id_receta`, `numero_paso`, `descripcion`) VALUES 
(1, 1, 'Cocinar la pasta en agua hirviendo con sal hasta que esté al dente'),
(1, 2, 'Mientras tanto, batir los huevos con el queso parmesano rallado'),
(1, 3, 'Sofreír el ajo picado en una sartén con un poco de aceite'),
(1, 4, 'Escurrir la pasta reservando un poco del agua de cocción'),
(1, 5, 'Mezclar la pasta caliente con los huevos batidos, añadiendo agua de pasta si es necesario'),
(1, 6, 'Servir inmediatamente con pimienta negra recién molida');

-- Paella (Receta 2)
INSERT INTO `Instrucciones` (`id_receta`, `numero_paso`, `descripcion`) VALUES 
(2, 1, 'Calentar aceite en una paellera y dorar los trozos de pollo'),
(2, 2, 'Añadir el tomate rallado y cocinar hasta que se evapore el líquido'),
(2, 3, 'Incorporar el arroz y remover durante 2 minutos'),
(2, 4, 'Añadir el caldo caliente y las especias, sin remover más'),
(2, 5, 'Cocinar a fuego medio-alto durante 10 minutos, luego bajar el fuego'),
(2, 6, 'Continuar cocinando 10 minutos más sin remover'),
(2, 7, 'Dejar reposar 5 minutos antes de servir');

-- Gazpacho (Receta 3)
INSERT INTO `Instrucciones` (`id_receta`, `numero_paso`, `descripcion`) VALUES 
(3, 1, 'Escaldar los tomates en agua hirviendo y pelarlos'),
(3, 2, 'Trocear todos los vegetales y ponerlos en la batidora'),
(3, 3, 'Añadir aceite de oliva, sal y un chorrito de vinagre'),
(3, 4, 'Batir hasta obtener una textura suave'),
(3, 5, 'Colar la mezcla para eliminar trozos'),
(3, 6, 'Refrigerar durante al menos 2 horas antes de servir');

-- Risotto (Receta 4)
INSERT INTO `Instrucciones` (`id_receta`, `numero_paso`, `descripcion`) VALUES 
(4, 1, 'Calentar el caldo y mantenerlo caliente durante toda la cocción'),
(4, 2, 'Sofreír la cebolla picada en mantequilla hasta que esté transparente'),
(4, 3, 'Añadir el arroz y tostar durante 2 minutos removiendo constantemente'),
(4, 4, 'Incorporar el caldo caliente cucharón a cucharón, removiendo hasta absorber'),
(4, 5, 'Continuar añadiendo caldo y removiendo durante 18-20 minutos'),
(4, 6, 'Finalizar con queso parmesano y mantequilla'),
(4, 7, 'Servir inmediatamente mientras está cremoso');

-- Tiramisu (Receta 5)
INSERT INTO `Instrucciones` (`id_receta`, `numero_paso`, `descripcion`) VALUES 
(5, 1, 'Separar las yemas de las claras de huevo'),
(5, 2, 'Batir las yemas con el azúcar hasta que estén pálidas'),
(5, 3, 'Montar las claras a punto de nieve'),
(5, 4, 'Preparar café fuerte y dejarlo enfriar'),
(5, 5, 'Incorporar las claras a la mezcla de yemas con movimientos envolventes'),
(5, 6, 'Mojar los bizcochos en café y crear capas alternando con la crema'),
(5, 7, 'Refrigerar durante al menos 4 horas'),
(5, 8, 'Espolvorear con cacao en polvo antes de servir');

-- Tacos de Pollo (Receta 6)
INSERT INTO `Instrucciones` (`id_receta`, `numero_paso`, `descripcion`) VALUES 
(6, 1, 'Marinar el pollo cortado en tiras con especias y limón durante 30 minutos'),
(6, 2, 'Calentar una sartén y cocinar el pollo hasta que esté dorado'),
(6, 3, 'Calentar las tortillas en una plancha o comal'),
(6, 4, 'Preparar el guacamole machacando el aguacate con limón y sal'),
(6, 5, 'Picar el cilantro finamente'),
(6, 6, 'Armar los tacos colocando pollo, guacamole y cilantro en cada tortilla');

-- Quinoa Bowl (Receta 7)
INSERT INTO `Instrucciones` (`id_receta`, `numero_paso`, `descripcion`) VALUES 
(7, 1, 'Cocinar el arroz según las instrucciones del paquete'),
(7, 2, 'Cortar las zanahorias en bastones y asar en el horno con aceite'),
(7, 3, 'Cocinar el brócoli al vapor hasta que esté tierno'),
(7, 4, 'Cortar el aguacate en láminas'),
(7, 5, 'Preparar un aderezo con limón y aceite de oliva'),
(7, 6, 'Servir todos los ingredientes en un bowl y aliñar');

-- Stir Fry (Receta 8)
INSERT INTO `Instrucciones` (`id_receta`, `numero_paso`, `descripcion`) VALUES 
(8, 1, 'Cortar todos los vegetales en tiras finas'),
(8, 2, 'Calentar aceite en un wok o sartén grande a fuego alto'),
(8, 3, 'Saltear el ajo durante 30 segundos'),
(8, 4, 'Añadir los vegetales más duros primero (zanahoria, brócoli)'),
(8, 5, 'Incorporar los pimientos al final'),
(8, 6, 'Servir inmediatamente mientras los vegetales estén crujientes');

-- Smoothie Bowl (Receta 9)
INSERT INTO `Instrucciones` (`id_receta`, `numero_paso`, `descripcion`) VALUES 
(9, 1, 'Congelar los plátanos cortados en rodajas la noche anterior'),
(9, 2, 'Batir los plátanos congelados con un poco de yogur hasta obtener consistencia cremosa'),
(9, 3, 'Cortar las fresas en láminas'),
(9, 4, 'Tostar la avena en una sartén seca hasta que esté dorada'),
(9, 5, 'Servir la mezcla de plátano en un bowl'),
(9, 6, 'Decorar con fresas, avena tostada y semillas al gusto');

-- Pollo Teriyaki (Receta 10)
INSERT INTO `Instrucciones` (`id_receta`, `numero_paso`, `descripcion`) VALUES 
(10, 1, 'Cortar el pollo en trozos medianos y sazonar con sal y pimienta'),
(10, 2, 'Preparar la salsa teriyaki mezclando azúcar, ajo picado y especias'),
(10, 3, 'Cocinar el arroz según las instrucciones del paquete'),
(10, 4, 'Dorar el pollo en una sartén con aceite hasta que esté cocido'),
(10, 5, 'Añadir la salsa teriyaki y cocinar hasta que espese'),
(10, 6, 'Servir el pollo sobre el arroz y decorar con semillas de sésamo');

-- Curry de Lentejas (Receta 11)
INSERT INTO `Instrucciones` (`id_receta`, `numero_paso`, `descripcion`) VALUES 
(11, 1, 'Enjuagar las lentejas rojas hasta que el agua salga clara'),
(11, 2, 'Sofreír la cebolla picada y el ajo en aceite hasta que estén dorados'),
(11, 3, 'Añadir las especias (comino, cúrcuma, paprika) y tostar durante 1 minuto'),
(11, 4, 'Incorporar las lentejas y cubrir con caldo o agua'),
(11, 5, 'Cocinar a fuego medio durante 15-20 minutos hasta que las lentejas estén tiernas'),
(11, 6, 'Añadir leche de coco y cocinar 5 minutos más'),
(11, 7, 'Ajustar sazón y servir con arroz o pan naan');

-- Overnight Oats (Receta 12)
INSERT INTO `Instrucciones` (`id_receta`, `numero_paso`, `descripcion`) VALUES 
(12, 1, 'Mezclar la avena con la leche en un frasco o recipiente'),
(12, 2, 'Añadir azúcar o endulzante al gusto'),
(12, 3, 'Incorporar las fresas cortadas en trozos pequeños'),
(12, 4, 'Remover bien todos los ingredientes'),
(12, 5, 'Tapar y refrigerar durante toda la noche'),
(12, 6, 'Por la mañana, servir frío y decorar con más frutas');

-- Ensalada de Garbanzos (Receta 13)
INSERT INTO `Instrucciones` (`id_receta`, `numero_paso`, `descripcion`) VALUES 
(13, 1, 'Escurrir y enjuagar los garbanzos de lata'),
(13, 2, 'Cortar los tomates en cubos medianos'),
(13, 3, 'Picar la cebolla finamente'),
(13, 4, 'Mezclar garbanzos, tomates y cebolla en un bowl grande'),
(13, 5, 'Preparar vinagreta con aceite de oliva, limón, sal y hierbas'),
(13, 6, 'Aliñar la ensalada y dejar reposar 10 minutos antes de servir');

-- Burger Vegana (Receta 14)
INSERT INTO `Instrucciones` (`id_receta`, `numero_paso`, `descripcion`) VALUES 
(14, 1, 'Escurrir y enjuagar los frijoles negros, luego machacarlos parcialmente'),
(14, 2, 'Sofreír la cebolla y el ajo picados hasta que estén transparentes'),
(14, 3, 'Mezclar los frijoles con la cebolla, avena y especias'),
(14, 4, 'Formar hamburguesas con la mezcla y refrigerar 30 minutos'),
(14, 5, 'Cocinar las hamburguesas en una sartén con aceite, 5 minutos por lado'),
(14, 6, 'Tostar los panes y armar las hamburguesas con vegetales frescos');

-- Brownie Vegano (Receta 15)
INSERT INTO `Instrucciones` (`id_receta`, `numero_paso`, `descripcion`) VALUES 
(15, 1, 'Precalentar el horno a 180°C y engrasar un molde cuadrado'),
(15, 2, 'Derretir el chocolate con aceite de oliva al baño maría'),
(15, 3, 'Mezclar harina, azúcar y cacao en polvo en un bowl'),
(15, 4, 'Incorporar el chocolate derretido a los ingredientes secos'),
(15, 5, 'Añadir un poco de agua si la mezcla está muy espesa'),
(15, 6, 'Verter en el molde y hornear durante 25-30 minutos'),
(15, 7, 'Dejar enfriar completamente antes de cortar');

-- 8. CREAR RELACIONES DE SEGUIMIENTO ENTRE USUARIOS
INSERT INTO `seguidores` (`usuario_id`, `seguidor_id`) VALUES 
(1, 2), -- Carlos sigue a María
(1, 3), -- Ana sigue a María
(2, 1), -- María sigue a Carlos
(2, 3), -- Ana sigue a Carlos
(3, 1); -- María sigue a Ana

-- 9. INSERTAR ALGUNOS "ME GUSTA" EN LAS RECETAS
INSERT INTO `Me_gusta` (`ususario_id`, `receta_id`) VALUES 
-- Me gustas de María (usuario 1)
(1, 6), (1, 7), (1, 11), (1, 12),
-- Me gustas de Carlos (usuario 2)
(2, 1), (2, 3), (2, 11), (2, 13), (2, 15),
-- Me gustas de Ana (usuario 3)
(3, 1), (3, 2), (3, 6), (3, 9), (3, 10);

-- 10. AGREGAR MÁS INGREDIENTES PARA COMPLETAR EL CATÁLOGO
INSERT INTO `Ingredientes` (`nombre`, `unidad_medida`) VALUES 
('Lentejas rojas', 'gramos'),
('Garbanzos', 'gramos'),
('Frijoles negros', 'gramos'),
('Leche de coco', 'ml'),
('Cúrcuma', 'cucharaditas'),
('Tahini', 'cucharadas'),
('Semillas de chía', 'cucharadas'),
('Granola', 'gramos'),
('Vinagre balsámico', 'ml'),
('Mostaza', 'cucharaditas'),
('Miel', 'cucharadas'),
('Jengibre', 'gramos'),
('Pimiento rojo', 'unidad'),
('Apio', 'tallos'),
('Pepino', 'unidad'),
('Rúcula', 'gramos'),
('Espinacas baby', 'gramos'),
('Champiñones', 'gramos'),
('Calabacín', 'unidad'),
('Berenjena', 'unidad');