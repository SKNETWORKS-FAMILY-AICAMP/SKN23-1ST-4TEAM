-- MySQL dump 10.13  Distrib 8.0.44, for Linux (x86_64)
--
-- Host: skn23-1st-4team.cr6u26mg6lbq.eu-north-1.rds.amazonaws.com    Database: SKN23
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `dim_age_group`
--

DROP TABLE IF EXISTS `dim_age_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dim_age_group` (
  `age_group_id` int unsigned NOT NULL AUTO_INCREMENT,
  `age_group` varchar(20) NOT NULL,
  `sort_order` tinyint unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`age_group_id`),
  UNIQUE KEY `uq_dim_age_group` (`age_group`),
  CONSTRAINT `chk_dim_age_group_sort_order` CHECK ((`sort_order` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dim_flow_subtype`
--

DROP TABLE IF EXISTS `dim_flow_subtype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dim_flow_subtype` (
  `subtype_id` int unsigned NOT NULL AUTO_INCREMENT,
  `subtype_name` varchar(100) NOT NULL,
  `group_name` varchar(20) NOT NULL DEFAULT '',
  `is_inheritance` char(1) NOT NULL DEFAULT 'N',
  `is_gift` char(1) NOT NULL DEFAULT 'N',
  PRIMARY KEY (`subtype_id`),
  UNIQUE KEY `uq_dim_flow_subtype` (`subtype_name`,`group_name`),
  CONSTRAINT `chk_dim_flow_subtype_gift` CHECK ((`is_gift` in (_utf8mb4'Y',_utf8mb4'N'))),
  CONSTRAINT `chk_dim_flow_subtype_inheritance` CHECK ((`is_inheritance` in (_utf8mb4'Y',_utf8mb4'N')))
) ENGINE=InnoDB AUTO_INCREMENT=168 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dim_fuel`
--

DROP TABLE IF EXISTS `dim_fuel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dim_fuel` (
  `fuel_id` int unsigned NOT NULL AUTO_INCREMENT,
  `fuel_name` varchar(30) NOT NULL,
  `is_eco` char(1) NOT NULL DEFAULT 'N',
  PRIMARY KEY (`fuel_id`),
  UNIQUE KEY `uq_dim_fuel` (`fuel_name`),
  CONSTRAINT `chk_dim_fuel_is_eco` CHECK ((`is_eco` in (_utf8mb4'Y',_utf8mb4'N')))
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dim_region_sido`
--

DROP TABLE IF EXISTS `dim_region_sido`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dim_region_sido` (
  `sido_id` int unsigned NOT NULL AUTO_INCREMENT,
  `sido_name` varchar(30) NOT NULL,
  `use_yn` char(1) NOT NULL DEFAULT 'Y',
  PRIMARY KEY (`sido_id`),
  UNIQUE KEY `uq_dim_region_sido_name` (`sido_name`),
  CONSTRAINT `chk_dim_region_sido_use_yn` CHECK ((`use_yn` in (_utf8mb4'Y',_utf8mb4'N')))
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dim_region_sigungu`
--

DROP TABLE IF EXISTS `dim_region_sigungu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dim_region_sigungu` (
  `sigungu_id` int unsigned NOT NULL AUTO_INCREMENT,
  `sido_id` int unsigned NOT NULL,
  `sigungu_name` varchar(50) NOT NULL,
  `use_yn` char(1) NOT NULL DEFAULT 'Y',
  PRIMARY KEY (`sigungu_id`),
  UNIQUE KEY `uq_dim_region_sigungu` (`sido_id`,`sigungu_name`),
  KEY `idx_sigungu_sido_id` (`sido_id`),
  CONSTRAINT `fk_sigungu_sido` FOREIGN KEY (`sido_id`) REFERENCES `dim_region_sido` (`sido_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `chk_dim_region_sigungu_use_yn` CHECK ((`use_yn` in (_utf8mb4'Y',_utf8mb4'N')))
) ENGINE=InnoDB AUTO_INCREMENT=1091 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `fact_flow_count`
--

DROP TABLE IF EXISTS `fact_flow_count`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fact_flow_count` (
  `flow_id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `year` int NOT NULL,
  `month` int NOT NULL,
  `sido_id` int unsigned NOT NULL,
  `flow_type` varchar(10) NOT NULL,
  `subtype_id` int unsigned NOT NULL,
  `vehicle_kind` varchar(10) DEFAULT NULL,
  `vehicle_kind_u` varchar(10) GENERATED ALWAYS AS (ifnull(`vehicle_kind`,_utf8mb4'_ALL_')) STORED,
  `is_cumulative` char(1) NOT NULL DEFAULT 'N',
  `flow_count` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`flow_id`),
  UNIQUE KEY `uq_fact_flow_count` (`year`,`month`,`sido_id`,`flow_type`,`subtype_id`,`vehicle_kind_u`,`is_cumulative`),
  KEY `idx_ffc_sido` (`sido_id`),
  KEY `idx_ffc_subtype` (`subtype_id`),
  KEY `idx_ffc_ym` (`year`,`month`),
  CONSTRAINT `fk_ffc_sido` FOREIGN KEY (`sido_id`) REFERENCES `dim_region_sido` (`sido_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_ffc_subtype` FOREIGN KEY (`subtype_id`) REFERENCES `dim_flow_subtype` (`subtype_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `chk_fact_flow_count_cum` CHECK ((`is_cumulative` in (_utf8mb4'Y',_utf8mb4'N')))
) ENGINE=InnoDB AUTO_INCREMENT=213045 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `fact_fuel_stock`
--

DROP TABLE IF EXISTS `fact_fuel_stock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fact_fuel_stock` (
  `fuel_stock_id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `year` int NOT NULL,
  `month` int NOT NULL,
  `sido_id` int unsigned NOT NULL,
  `fuel_id` int unsigned NOT NULL,
  `vehicle_kind` varchar(10) NOT NULL,
  `business_type` varchar(10) NOT NULL,
  `stock_count` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`fuel_stock_id`),
  UNIQUE KEY `uq_fact_fuel_stock` (`year`,`month`,`sido_id`,`fuel_id`,`vehicle_kind`,`business_type`),
  KEY `idx_ffs_sido` (`sido_id`),
  KEY `idx_ffs_fuel` (`fuel_id`),
  KEY `idx_ffs_ym` (`year`,`month`),
  CONSTRAINT `fk_ffs_fuel` FOREIGN KEY (`fuel_id`) REFERENCES `dim_fuel` (`fuel_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_ffs_sido` FOREIGN KEY (`sido_id`) REFERENCES `dim_region_sido` (`sido_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=86412 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `fact_owner_demo_stock`
--

DROP TABLE IF EXISTS `fact_owner_demo_stock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fact_owner_demo_stock` (
  `demo_id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `year` int NOT NULL,
  `month` int NOT NULL,
  `sido_id` int unsigned NOT NULL,
  `gender` varchar(10) NOT NULL,
  `age_group_id` int unsigned NOT NULL,
  `stock_count` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`demo_id`),
  UNIQUE KEY `uq_fact_owner_demo_stock` (`year`,`month`,`sido_id`,`gender`,`age_group_id`),
  KEY `idx_fods_sido` (`sido_id`),
  KEY `idx_fods_age` (`age_group_id`),
  KEY `idx_fods_ym` (`year`,`month`),
  CONSTRAINT `fk_fods_age` FOREIGN KEY (`age_group_id`) REFERENCES `dim_age_group` (`age_group_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_fods_sido` FOREIGN KEY (`sido_id`) REFERENCES `dim_region_sido` (`sido_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5237 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `fact_recall`
--

DROP TABLE IF EXISTS `fact_recall`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fact_recall` (
  `recall_id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `recall_date` date NOT NULL,
  `maker_name` varchar(100) NOT NULL,
  `car_name` varchar(100) NOT NULL,
  `prod_start_date` date DEFAULT NULL,
  `prod_end_date` date DEFAULT NULL,
  `fix_start_date` date DEFAULT NULL,
  `fix_end_date` date DEFAULT NULL,
  `target_count` int unsigned DEFAULT NULL,
  `remedy_method` text,
  `uniq_hash` char(64) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`recall_id`),
  UNIQUE KEY `uq_fact_recall_hash` (`uniq_hash`),
  KEY `idx_fact_recall_date` (`recall_date`),
  KEY `idx_fact_recall_maker` (`maker_name`),
  KEY `idx_fact_recall_car` (`car_name`),
  CONSTRAINT `chk_fact_recall_fix_range` CHECK (((`fix_start_date` is null) or (`fix_end_date` is null) or (`fix_start_date` <= `fix_end_date`))),
  CONSTRAINT `chk_fact_recall_prod_range` CHECK (((`prod_start_date` is null) or (`prod_end_date` is null) or (`prod_start_date` <= `prod_end_date`))),
  CONSTRAINT `chk_fact_recall_target_count` CHECK (((`target_count` is null) or (`target_count` >= 0)))
) ENGINE=InnoDB AUTO_INCREMENT=346 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `fact_vehicle_stock`
--

DROP TABLE IF EXISTS `fact_vehicle_stock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fact_vehicle_stock` (
  `stock_id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `year` int NOT NULL,
  `month` int NOT NULL,
  `origin_type` varchar(10) NOT NULL,
  `sido_id` int unsigned NOT NULL,
  `vehicle_kind` varchar(10) NOT NULL,
  `usage_type` varchar(10) NOT NULL,
  `stock_count` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`stock_id`),
  UNIQUE KEY `uq_fact_vehicle_stock` (`year`,`month`,`origin_type`,`sido_id`,`vehicle_kind`,`usage_type`),
  KEY `idx_fvs_sido` (`sido_id`),
  KEY `idx_fvs_ym` (`year`,`month`),
  CONSTRAINT `fk_fvs_sido` FOREIGN KEY (`sido_id`) REFERENCES `dim_region_sido` (`sido_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5101 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `faq`
--

DROP TABLE IF EXISTS `faq`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `faq` (
  `faq_id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `brand` varchar(50) NOT NULL,
  `category` varchar(100) DEFAULT NULL,
  `question` varchar(100) NOT NULL,
  `answer` text NOT NULL,
  `uniq_hash` char(64) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`faq_id`),
  UNIQUE KEY `uq_faq_hash` (`uniq_hash`),
  KEY `idx_faq_brand` (`brand`),
  KEY `idx_faq_brand_category` (`brand`,`category`)
) ENGINE=InnoDB AUTO_INCREMENT=167 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'SKN23'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-21 14:12:41
