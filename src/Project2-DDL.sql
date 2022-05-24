CREATE DATABASE MY_CUSTOM_BOT
     CHARACTER SET utf8mb4
     COLLATE utf8mb4_unicode_ci;
commit; 

USE MY_CUSTOM_BOT;

CREATE TABLE `engines` (
  `engine_id` smallint(3) NOT NULL AUTO_INCREMENT,
  `engine` varchar(45) NOT NULL,
  PRIMARY KEY (`engine_id`)
);

CREATE TABLE `keywords` (
  `keyword_id` int(11) NOT NULL AUTO_INCREMENT,
  `keyword` varchar(255) NOT NULL,
  PRIMARY KEY (`keyword_id`)
);

CREATE TABLE `stg_results` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `engine_id` smallint(3) NOT NULL,
  `keyword_id` int(11) NOT NULL,
  `page` smallint(5) NOT NULL DEFAULT '1',
  `ad_flag` tinyint(1) NOT NULL DEFAULT '0',
  `title` varchar(255) NOT NULL,
  `link` text NOT NULL,
  `path` text,
  `description` text,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `stg_result_engine_id_foreign_idx` (`engine_id`),
  KEY `stg_result_keyword_id_foreign_idx` (`keyword_id`),
  CONSTRAINT `stg_results_engine_id_foreign` FOREIGN KEY (`engine_id`) REFERENCES `engines` (`engine_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `stg_results_keyword_id_foreign` FOREIGN KEY (`keyword_id`) REFERENCES `keywords` (`keyword_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
);

CREATE TABLE `pub_results` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `keyword_id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `link` text NOT NULL,
  `path` text,
  `description` text,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `pub_results_keyword_id_foreign_idx` (`keyword_id`),
  CONSTRAINT `pub_results_keyword_id_foreign` FOREIGN KEY (`keyword_id`) REFERENCES `keywords` (`keyword_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
);

CREATE TABLE `result_details` (
  `result_id` bigint(20) unsigned NOT NULL,
  `link_type` varchar(20) NOT NULL,
  `info_type` varchar(20) NOT NULL,
  `content_details` longtext,
  `frequency` int(11) NOT NULL,
  `each_frequency` varchar(255) NOT NULL,
  `status` varchar(45) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY `result_details_result_id_foreign_idx_idx` (`result_id`),
  CONSTRAINT `result_details_result_id_foreign_idx` FOREIGN KEY (`result_id`) REFERENCES `pub_results` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
);

commit; 

INSERT INTO `engines` (`engine`) VALUES ('Google');
INSERT INTO `engines` (`engine`) VALUES ('Yahoo');
INSERT INTO `engines` (`engine`) VALUES ('Bing');
commit; 
