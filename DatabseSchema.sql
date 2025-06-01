CREATE DATABASE  IF NOT EXISTS `pharmacy_2.0` /*!40100 DEFAULT CHARACTER SET utf8mb3 */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `pharmacy_2.0`;
-- MySQL dump 10.13  Distrib 8.0.38, for Win64 (x86_64)
--
-- Host: localhost    Database: pharmacy_2.0
-- ------------------------------------------------------
-- Server version	8.0.39

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
-- Temporary view structure for view `account_details`
--

DROP TABLE IF EXISTS `account_details`;
/*!50001 DROP VIEW IF EXISTS `account_details`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `account_details` AS SELECT 
 1 AS `AC_id`,
 1 AS `user`,
 1 AS `manager`,
 1 AS `email`,
 1 AS `FB_id`,
 1 AS `PH_id`,
 1 AS `phname`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `accounts`
--

DROP TABLE IF EXISTS `accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts` (
  `AC_id` int NOT NULL AUTO_INCREMENT,
  `user` varchar(50) NOT NULL DEFAULT ' ',
  `Manager` enum('Yes','No') NOT NULL,
  `email` varchar(100) NOT NULL,
  `FB_ID` varchar(128) NOT NULL,
  PRIMARY KEY (`AC_id`),
  UNIQUE KEY `id_UNIQUE` (`AC_id`),
  UNIQUE KEY `FB_ID_UNIQUE` (`FB_ID`),
  UNIQUE KEY `email_UNIQUE` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `admins`
--

DROP TABLE IF EXISTS `admins`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admins` (
  `Admin_id` varchar(128) NOT NULL,
  `Password` varchar(64) NOT NULL,
  `medAccess` enum('Yes','No') NOT NULL,
  `pharmaAccess` enum('Yes','No') NOT NULL,
  PRIMARY KEY (`Admin_id`),
  UNIQUE KEY `AdminName_UNIQUE` (`Admin_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `batch`
--

DROP TABLE IF EXISTS `batch`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `batch` (
  `item_id` bigint NOT NULL,
  `EXDate` date NOT NULL,
  `count` int unsigned NOT NULL,
  PRIMARY KEY (`item_id`,`EXDate`),
  CONSTRAINT `fk_batch_Stock1` FOREIGN KEY (`item_id`) REFERENCES `stockitems` (`Item_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ddi`
--

DROP TABLE IF EXISTS `ddi`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ddi` (
  `TA1_id` int NOT NULL,
  `TA2_id` int NOT NULL,
  `DDI_effect` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`TA1_id`,`TA2_id`),
  KEY `fk_DDI_TA2` (`TA2_id`),
  CONSTRAINT `fk_DDI_TA1` FOREIGN KEY (`TA1_id`) REFERENCES `ta` (`TA_id`),
  CONSTRAINT `fk_DDI_TA2` FOREIGN KEY (`TA2_id`) REFERENCES `ta` (`TA_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dosage`
--

DROP TABLE IF EXISTS `dosage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dosage` (
  `MED_id` int NOT NULL,
  `TA_id` int NOT NULL,
  `unit` enum('g','ml/g','ml/ml','g/g','meq/ml','mcg/ml','mcg/g','mg','mcg','mg/ml','mg/g','W/W %','W/V %','V/V %','UI') NOT NULL,
  `concetration` int NOT NULL,
  PRIMARY KEY (`MED_id`,`TA_id`),
  KEY `fk_MED_has_TA_TA1_idx` (`TA_id`),
  KEY `fk_MED_has_TA_MED1_idx` (`MED_id`),
  CONSTRAINT `fk_MED_has_TA_MED1` FOREIGN KEY (`MED_id`) REFERENCES `med` (`MED_id`),
  CONSTRAINT `fk_MED_has_TA_TA1` FOREIGN KEY (`TA_id`) REFERENCES `ta` (`TA_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `manufacturer`
--

DROP TABLE IF EXISTS `manufacturer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `manufacturer` (
  `Manufacturer_id` int NOT NULL AUTO_INCREMENT,
  `Manufacturer` varchar(50) NOT NULL,
  `country` varchar(50) NOT NULL,
  PRIMARY KEY (`Manufacturer_id`),
  UNIQUE KEY `id_UNIQUE` (`Manufacturer_id`),
  UNIQUE KEY `Manufacturer_UNIQUE` (`Manufacturer`),
  KEY `index` (`country`,`Manufacturer`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `med`
--

DROP TABLE IF EXISTS `med`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `med` (
  `MED_id` int NOT NULL AUTO_INCREMENT,
  `Description` varchar(1024) DEFAULT ' ',
  `Brand` enum('Yes','No') NOT NULL,
  `Med` varchar(100) NOT NULL,
  `Manufacturer_id` int NOT NULL,
  `POM` enum('Yes','No') NOT NULL,
  `DosageForm` enum('TABLET','CAPSULE','SYRUP','SUSPENSION','INJECTION','OINTMENT','CREAM','GEL','DROPS','INHALER','SPRAY','PATCH','POWDER','SOLUTION','SUPPOSITORY','EMULSION','LOZENGE','TROCHE','NASAL_SPRAY','EYE_DROPS','EAR_DROPS','TRANSDERMAL_PATCH','MUCOADHESIVE_FILM','MISC') NOT NULL,
  `Obsolete` enum('Yes','No') NOT NULL DEFAULT 'No',
  PRIMARY KEY (`MED_id`),
  UNIQUE KEY `id_UNIQUE` (`MED_id`),
  UNIQUE KEY `Med_UNIQUE` (`Med`),
  KEY `fk_MED_Manufacturer1_idx` (`Manufacturer_id`),
  KEY `Index` (`MED_id`,`Med`),
  CONSTRAINT `fk_MED_Manufacturer1` FOREIGN KEY (`Manufacturer_id`) REFERENCES `manufacturer` (`Manufacturer_id`)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `med_details`
--

DROP TABLE IF EXISTS `med_details`;
/*!50001 DROP VIEW IF EXISTS `med_details`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `med_details` AS SELECT 
 1 AS `Med_id`,
 1 AS `Med`,
 1 AS `POM`,
 1 AS `effSystems`,
 1 AS `TAs`,
 1 AS `TA_ids`,
 1 AS `Addiction`,
 1 AS `concentrations`,
 1 AS `units`,
 1 AS `Brand`,
 1 AS `country`,
 1 AS `manufacturer`,
 1 AS `Form`,
 1 AS `Obsolete`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `medid_ta`
--

DROP TABLE IF EXISTS `medid_ta`;
/*!50001 DROP VIEW IF EXISTS `medid_ta`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `medid_ta` AS SELECT 
 1 AS `Med_id`,
 1 AS `TA`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `medlist`
--

DROP TABLE IF EXISTS `medlist`;
/*!50001 DROP VIEW IF EXISTS `medlist`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `medlist` AS SELECT 
 1 AS `MED_id`,
 1 AS `Med`,
 1 AS `Brand`,
 1 AS `POM`,
 1 AS `Manufacturer`,
 1 AS `country`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `ph_ac`
--

DROP TABLE IF EXISTS `ph_ac`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ph_ac` (
  `PH_id` int NOT NULL,
  `AC_id` int NOT NULL,
  PRIMARY KEY (`PH_id`,`AC_id`),
  KEY `fk_PH_AC_Accounts1_idx` (`AC_id`),
  CONSTRAINT `fk_PH_AC_Accounts1` FOREIGN KEY (`AC_id`) REFERENCES `accounts` (`AC_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_PH_AC_Pharmacies1` FOREIGN KEY (`PH_id`) REFERENCES `pharmacies` (`PH_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pharmacies`
--

DROP TABLE IF EXISTS `pharmacies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pharmacies` (
  `PH_id` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(50) NOT NULL,
  PRIMARY KEY (`PH_id`),
  UNIQUE KEY `id_UNIQUE` (`PH_id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `pharmacy_details`
--

DROP TABLE IF EXISTS `pharmacy_details`;
/*!50001 DROP VIEW IF EXISTS `pharmacy_details`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `pharmacy_details` AS SELECT 
 1 AS `AC_id`,
 1 AS `user`,
 1 AS `manager`,
 1 AS `email`,
 1 AS `FB_id`,
 1 AS `PH_id`,
 1 AS `phname`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `selllogs`
--

DROP TABLE IF EXISTS `selllogs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `selllogs` (
  `SELL_id` bigint NOT NULL AUTO_INCREMENT,
  `date` datetime NOT NULL,
  `ph_id` int NOT NULL,
  `content` text,
  PRIMARY KEY (`SELL_id`),
  UNIQUE KEY `id_UNIQUE` (`SELL_id`),
  KEY `fk_SellLogs_Pharmacies1_idx` (`ph_id`),
  CONSTRAINT `fk_SellLogs_Pharmacies1` FOREIGN KEY (`ph_id`) REFERENCES `pharmacies` (`PH_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `stock_list`
--

DROP TABLE IF EXISTS `stock_list`;
/*!50001 DROP VIEW IF EXISTS `stock_list`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `stock_list` AS SELECT 
 1 AS `Ph_id`,
 1 AS `Item_id`,
 1 AS `Med_id`,
 1 AS `Med`,
 1 AS `Brand`,
 1 AS `Pom`,
 1 AS `Obsolete`,
 1 AS `Manufacturer`,
 1 AS `Country`,
 1 AS `Price`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `stockitems`
--

DROP TABLE IF EXISTS `stockitems`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stockitems` (
  `Item_id` bigint NOT NULL AUTO_INCREMENT,
  `Ph_id` int NOT NULL,
  `price` int NOT NULL,
  `Med_id` int NOT NULL,
  PRIMARY KEY (`Item_id`),
  UNIQUE KEY `Item_id_UNIQUE` (`Item_id`),
  UNIQUE KEY `ph_med` (`Ph_id`,`Med_id`),
  KEY `fk_Stock_Pharmacies1_idx` (`Ph_id`),
  KEY `fk_Stock_med1_idx` (`Med_id`),
  CONSTRAINT `fk_Stock_med1` FOREIGN KEY (`Med_id`) REFERENCES `med` (`MED_id`),
  CONSTRAINT `fk_Stock_Pharmacies1` FOREIGN KEY (`Ph_id`) REFERENCES `pharmacies` (`PH_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=123 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ta`
--

DROP TABLE IF EXISTS `ta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ta` (
  `TA_id` int NOT NULL AUTO_INCREMENT,
  `SystemEffect` enum('CentralNervous','PeripheralNervous','Infections','Tumors','Cardiovascular','Dermatological','Gastrointestinl','Endocrine','Musculoskeletal','Ophthalmic','Urinary','Immune','Respiratory','Blood-Nutrition','Reproductive','Inflammation','Ear-Nose-Oropharnyx','Misc') NOT NULL,
  `DrugofAbuse` enum('Yes','No') NOT NULL,
  `TA` varchar(100) NOT NULL,
  `SE` varchar(1024) DEFAULT ' ',
  `CC` varchar(1024) DEFAULT ' ',
  `FC` varchar(1024) DEFAULT ' ',
  PRIMARY KEY (`TA_id`),
  UNIQUE KEY `id_UNIQUE` (`TA_id`),
  UNIQUE KEY `TA_UNIQUE` (`TA`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `ta_ddi`
--

DROP TABLE IF EXISTS `ta_ddi`;
/*!50001 DROP VIEW IF EXISTS `ta_ddi`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `ta_ddi` AS SELECT 
 1 AS `TA_id`,
 1 AS `Interaction`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `ticket`
--

DROP TABLE IF EXISTS `ticket`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ticket` (
  `TK_id` bigint NOT NULL AUTO_INCREMENT,
  `Content` text NOT NULL,
  `Date` date NOT NULL,
  `Account` varchar(128) NOT NULL,
  `Pharmacy` int NOT NULL,
  `Med` int NOT NULL DEFAULT '0',
  `State` enum('Wait','Complete','Discard') NOT NULL,
  PRIMARY KEY (`TK_id`),
  UNIQUE KEY `id_UNIQUE` (`TK_id`),
  KEY `fk_Ticket_Pharmacies_idx` (`Pharmacy`),
  KEY `fk_Ticket_Med_idx` (`Med`),
  KEY `fk_Ticket_Acount_idx` (`Account`),
  CONSTRAINT `fk_Ticket_Accounts` FOREIGN KEY (`Account`) REFERENCES `accounts` (`FB_ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_Ticket_Med` FOREIGN KEY (`Med`) REFERENCES `med` (`MED_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_Ticket_Pharmacies` FOREIGN KEY (`Pharmacy`) REFERENCES `pharmacies` (`PH_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `updatelog`
--

DROP TABLE IF EXISTS `updatelog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `updatelog` (
  `UP_id` bigint NOT NULL AUTO_INCREMENT,
  `date` datetime NOT NULL,
  `ph_id` int NOT NULL,
  `content` text,
  PRIMARY KEY (`UP_id`),
  UNIQUE KEY `id_UNIQUE` (`UP_id`),
  KEY `fk_UpdatelLog_Pharmacies1_idx` (`ph_id`),
  CONSTRAINT `fk_UpdatelLog_Pharmacies1` FOREIGN KEY (`ph_id`) REFERENCES `pharmacies` (`PH_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=156 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Final view structure for view `account_details`
--

/*!50001 DROP VIEW IF EXISTS `account_details`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `account_details` AS select `accounts`.`AC_id` AS `AC_id`,`accounts`.`user` AS `user`,`accounts`.`Manager` AS `manager`,`accounts`.`email` AS `email`,`accounts`.`FB_ID` AS `FB_id`,`pharmacies`.`PH_id` AS `PH_id`,`pharmacies`.`Name` AS `phname` from ((`accounts` left join `ph_ac` on((`accounts`.`AC_id` = `ph_ac`.`AC_id`))) left join `pharmacies` on((`ph_ac`.`PH_id` = `pharmacies`.`PH_id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `med_details`
--

/*!50001 DROP VIEW IF EXISTS `med_details`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `med_details` AS select `med`.`MED_id` AS `Med_id`,`med`.`Med` AS `Med`,`med`.`POM` AS `POM`,group_concat(`ta`.`SystemEffect` order by `dosage`.`TA_id` ASC separator ',') AS `effSystems`,group_concat(`ta`.`TA` order by `dosage`.`TA_id` ASC separator ',') AS `TAs`,group_concat(`ta`.`TA_id` order by `dosage`.`TA_id` ASC separator ',') AS `TA_ids`,group_concat(`ta`.`DrugofAbuse` order by `dosage`.`TA_id` ASC separator ',') AS `Addiction`,group_concat(`dosage`.`concetration` order by `dosage`.`TA_id` ASC separator ',') AS `concentrations`,group_concat(`dosage`.`unit` order by `dosage`.`TA_id` ASC separator ',') AS `units`,`med`.`Brand` AS `Brand`,`manufacturer`.`country` AS `country`,`manufacturer`.`Manufacturer` AS `manufacturer`,`med`.`DosageForm` AS `Form`,`med`.`Obsolete` AS `Obsolete` from (((`med` join `manufacturer` on((`med`.`Manufacturer_id` = `manufacturer`.`Manufacturer_id`))) left join `dosage` on((`med`.`MED_id` = `dosage`.`MED_id`))) left join `ta` on((`dosage`.`TA_id` = `ta`.`TA_id`))) group by `med`.`MED_id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `medid_ta`
--

/*!50001 DROP VIEW IF EXISTS `medid_ta`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `medid_ta` AS select `dosage`.`MED_id` AS `Med_id`,`ta`.`TA` AS `TA` from ((`ta` join `dosage` on((`ta`.`TA_id` = `dosage`.`TA_id`))) join `med` on((`dosage`.`MED_id` = `med`.`MED_id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `medlist`
--

/*!50001 DROP VIEW IF EXISTS `medlist`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `medlist` AS select `med`.`MED_id` AS `MED_id`,`med`.`Med` AS `Med`,`med`.`Brand` AS `Brand`,`med`.`POM` AS `POM`,`manufacturer`.`Manufacturer` AS `Manufacturer`,`manufacturer`.`country` AS `country` from (`med` left join `manufacturer` on((`med`.`Manufacturer_id` = `manufacturer`.`Manufacturer_id`))) where (`med`.`Obsolete` = 'No') order by `med`.`MED_id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `pharmacy_details`
--

/*!50001 DROP VIEW IF EXISTS `pharmacy_details`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `pharmacy_details` AS select `accounts`.`AC_id` AS `AC_id`,`accounts`.`user` AS `user`,`accounts`.`Manager` AS `manager`,`accounts`.`email` AS `email`,`accounts`.`FB_ID` AS `FB_id`,`pharmacies`.`PH_id` AS `PH_id`,`pharmacies`.`Name` AS `phname` from ((`pharmacies` left join `ph_ac` on((`ph_ac`.`PH_id` = `pharmacies`.`PH_id`))) left join `accounts` on((`accounts`.`AC_id` = `ph_ac`.`AC_id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `stock_list`
--

/*!50001 DROP VIEW IF EXISTS `stock_list`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `stock_list` AS select `stockitems`.`Ph_id` AS `Ph_id`,`stockitems`.`Item_id` AS `Item_id`,`stockitems`.`Med_id` AS `Med_id`,`med`.`Med` AS `Med`,`med`.`Brand` AS `Brand`,`med`.`POM` AS `Pom`,`med`.`Obsolete` AS `Obsolete`,`manufacturer`.`Manufacturer` AS `Manufacturer`,`manufacturer`.`country` AS `Country`,`stockitems`.`price` AS `Price` from ((`stockitems` left join `med` on((`stockitems`.`Med_id` = `med`.`MED_id`))) left join `manufacturer` on((`med`.`Manufacturer_id` = `manufacturer`.`Manufacturer_id`))) order by `stockitems`.`Item_id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `ta_ddi`
--

/*!50001 DROP VIEW IF EXISTS `ta_ddi`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `ta_ddi` AS select `ddi`.`TA1_id` AS `TA_id`,`ta`.`TA` AS `Interaction` from (`ta` join `ddi`) where (`ta`.`TA_id` = `ddi`.`TA2_id`) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-22 13:14:45
