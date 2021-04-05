SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

CREATE DATABASE IF NOT EXISTS `derebit_bot`;

USE `derebit_bot`;

CREATE TABLE IF NOT EXISTS `log` (
	`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
	`create` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`sender_id` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Имя модуля или программы создавшей лог' COLLATE 'utf8mb4_0900_ai_ci',
	`level` VARCHAR(25) NOT NULL COMMENT 'Тип записи' COLLATE 'utf8mb4_0900_ai_ci',
	`level_order` TINYINT(3) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Значимый вес',
	`data` TEXT NOT NULL COMMENT 'Текст лога' COLLATE 'utf8mb4_0900_ai_ci',
	PRIMARY KEY (`id`) USING BTREE,
	INDEX `create` (`create`) USING BTREE,
	INDEX `sender_id` (`sender_id`) USING BTREE,
	INDEX `level` (`level`) USING BTREE,
	INDEX `level_order` (`level_order`) USING BTREE
)
COMMENT='Содержит логи работы бота'
COLLATE='utf8mb4_0900_ai_ci'
ENGINE=InnoDB
;

CREATE TABLE IF NOT EXISTS `order` (
	`id` VARCHAR(25) NOT NULL COMMENT 'ID, используется id с биржи' COLLATE 'utf8mb4_0900_ai_ci',
	`active` TINYINT(3) UNSIGNED NOT NULL DEFAULT '1' COMMENT '1 - управляется ботом, 0 - не управляется, 2 - управление потеряно (т.е. например: при загрузке ордер не нашелся)',
	`group_id` VARCHAR(64) NOT NULL COMMENT 'ID объединяет группу ордеров buy и sell (такое-же значение попадает в label у ордера)' COLLATE 'utf8mb4_0900_ai_ci',
	`instrument` VARCHAR(25) NOT NULL COMMENT 'Инструмент' COLLATE 'utf8mb4_0900_ai_ci',
	`state` VARCHAR(15) NOT NULL COMMENT 'Статус на бирже' COLLATE 'utf8mb4_0900_ai_ci',
	`type` VARCHAR(15) NOT NULL COMMENT 'Тип (limit, market и т.п.)' COLLATE 'utf8mb4_0900_ai_ci',
	`direction` VARCHAR(5) NOT NULL COMMENT 'Направление buy или sell' COLLATE 'utf8mb4_0900_ai_ci',
	`price` DECIMAL(10,2) UNSIGNED NOT NULL DEFAULT '0.00' COMMENT 'Цена входа',
	`amount` DECIMAL(10,2) UNSIGNED NOT NULL DEFAULT '0.00' COMMENT 'Объем по ордеру',
	`real_create` DATETIME NOT NULL COMMENT 'Дата и время создания на бирже',
	`real_update` DATETIME NULL DEFAULT NULL COMMENT 'Дата и время последнего обновления на бирже',
	`create` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Дата и время создания, ботом',
	`update` DATETIME NULL DEFAULT NULL COMMENT 'Дата и время последнего обновления, ботом',
	`raw_data` TEXT NULL DEFAULT NULL COMMENT 'Текст исходного JSON объекта ордера' COLLATE 'utf8mb4_0900_ai_ci',
	`last_raw_data` TEXT NULL DEFAULT NULL COMMENT 'Текст исходного JSON последнего объекта ордера' COLLATE 'utf8mb4_0900_ai_ci',
	`active_comment` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Комментарий по присвоенному статусу active (Например: order not find)' COLLATE 'utf8mb4_0900_ai_ci',
	PRIMARY KEY (`id`) USING BTREE,
	INDEX `active` (`active`) USING BTREE,
	INDEX `create` (`create`) USING BTREE,
	INDEX `real_create` (`real_create`) USING BTREE,
	INDEX `real_update` (`real_update`) USING BTREE,
	INDEX `update` (`update`) USING BTREE,
	INDEX `instrument` (`instrument`) USING BTREE,
	INDEX `group_id` (`group_id`) USING BTREE
)
COMMENT='Таблица ордеров, созданные и ведомые ботом (базовые понятия о типах, были взяты с типов данных биржи Deribit)'
COLLATE='utf8mb4_0900_ai_ci'
ENGINE=InnoDB
;
