CREATE DATABASE `itinerarygen`;

CREATE TABLE `attractions` (
  `id` bigint(7) NOT NULL AUTO_INCREMENT,
  `url` varchar(200) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `reviews` varchar(15) DEFAULT NULL,
  `rating` varchar(15) DEFAULT NULL,
  `category` varchar(30) DEFAULT NULL,
  `created` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `modified` date DEFAULT NULL,
  `city` varchar(50) DEFAULT NULL,
  `country` varchar(40) DEFAULT NULL,
  `latitude` varchar(40) DEFAULT NULL,
  `longitude` varchar(40) DEFAULT NULL,
  `country1` varchar(40) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=166812 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `pages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(255) NOT NULL,
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `numresults` int(11) DEFAULT NULL,
  `numpages` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=54635 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `hw_countrylinks` (
  `id` int(6) NOT NULL AUTO_INCREMENT,
  `url` varchar(80) DEFAULT NULL,
  `modified` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=140 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `hw_hotels` (
  `id` int(6) NOT NULL AUTO_INCREMENT,
  `url` varchar(120) DEFAULT NULL,
  `name` varchar(80) DEFAULT NULL,
  `price` double DEFAULT NULL,
  `reviews` int(11) DEFAULT NULL,
  `rating` double DEFAULT NULL,
  `latitude` float DEFAULT NULL,
  `longitude` float DEFAULT NULL,
  `modified` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `city` varchar(40) DEFAULT NULL,
  `country` varchar(40) DEFAULT NULL,
  `country1` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1526 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci