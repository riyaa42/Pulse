-- MySQL dump 10.13  Distrib 8.0.45, for Win64 (x86_64)
--
-- Host: localhost    Database: musicdb
-- ------------------------------------------------------
-- Server version	8.0.45

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
-- Table structure for table `album`
--

DROP TABLE IF EXISTS `album`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `album` (
  `AlbumID` int NOT NULL AUTO_INCREMENT,
  `Title` varchar(100) NOT NULL,
  `ReleaseDate` date DEFAULT NULL,
  `Language` varchar(50) DEFAULT NULL,
  `AlbumType` varchar(50) DEFAULT NULL,
  `CoverImage` varchar(255) NOT NULL,
  PRIMARY KEY (`AlbumID`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `album`
--

LOCK TABLES `album` WRITE;
/*!40000 ALTER TABLE `album` DISABLE KEYS */;
INSERT INTO `album` VALUES (1,'Aashiqui 2','2013-04-26','Hindi','Soundtrack','aashiqui2.jpg'),(2,'1989','2014-10-27','English','Studio Album','1989.jpg'),(3,'Scorpion','2018-06-29','English','Studio Album','scorpion.jpg'),(4,'Devdas','2002-07-12','Hindi','Soundtrack','devdas.jpg'),(5,'After Hours','2020-03-20','English','Studio Album','afterhours.jpg');
/*!40000 ALTER TABLE `album` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `albumtag`
--

DROP TABLE IF EXISTS `albumtag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `albumtag` (
  `Album_AlbumID` int NOT NULL,
  `Tag_TagID` int NOT NULL,
  PRIMARY KEY (`Album_AlbumID`,`Tag_TagID`),
  KEY `fk_AlbumTag_Album1_idx` (`Album_AlbumID`),
  KEY `fk_AlbumTag_Tag1_idx` (`Tag_TagID`),
  CONSTRAINT `fk_AlbumTag_Album1` FOREIGN KEY (`Album_AlbumID`) REFERENCES `album` (`AlbumID`),
  CONSTRAINT `fk_AlbumTag_Tag1` FOREIGN KEY (`Tag_TagID`) REFERENCES `tag` (`TagID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `albumtag`
--

LOCK TABLES `albumtag` WRITE;
/*!40000 ALTER TABLE `albumtag` DISABLE KEYS */;
INSERT INTO `albumtag` VALUES (1,1),(2,2),(3,3),(4,4),(5,2),(5,5);
/*!40000 ALTER TABLE `albumtag` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `artist`
--

DROP TABLE IF EXISTS `artist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `artist` (
  `ArtistID` int NOT NULL AUTO_INCREMENT,
  `StageName` varchar(100) NOT NULL,
  `FirstName` varchar(50) DEFAULT NULL,
  `LastName` varchar(50) DEFAULT NULL,
  `Bio` longtext,
  `Country` varchar(50) DEFAULT NULL,
  `VerificationStatus` varchar(20) NOT NULL,
  `CreatedAt` datetime NOT NULL,
  `ProfileImage` varchar(255) NOT NULL,
  PRIMARY KEY (`ArtistID`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `artist`
--

LOCK TABLES `artist` WRITE;
/*!40000 ALTER TABLE `artist` DISABLE KEYS */;
INSERT INTO `artist` VALUES (1,'Arijit Singh','Arijit','Singh','Popular Indian playback singer','India','Verified','2026-04-06 00:37:43','arijit.jpg'),(2,'Taylor Swift','Taylor','Swift','American singer-songwriter','USA','Verified','2026-04-06 00:37:43','taylor.jpg'),(3,'Drake','Aubrey','Graham','Canadian rapper and singer','Canada','Verified','2026-04-06 00:37:43','drake.jpg'),(4,'Shreya Ghoshal','Shreya','Ghoshal','Indian playback singer','India','Verified','2026-04-06 00:37:43','shreya.jpg'),(5,'The Weeknd','Abel','Tesfaye','Canadian singer and performer','Canada','Verified','2026-04-06 00:37:43','weeknd.jpg');
/*!40000 ALTER TABLE `artist` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `artistalbum`
--

DROP TABLE IF EXISTS `artistalbum`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `artistalbum` (
  `Album_AlbumID` int NOT NULL,
  `Artist_ArtistID` int NOT NULL,
  PRIMARY KEY (`Album_AlbumID`,`Artist_ArtistID`),
  KEY `fk_ArtistAlbum_Album1_idx` (`Album_AlbumID`),
  KEY `fk_ArtistAlbum_Artist1_idx` (`Artist_ArtistID`),
  CONSTRAINT `fk_ArtistAlbum_Album1` FOREIGN KEY (`Album_AlbumID`) REFERENCES `album` (`AlbumID`),
  CONSTRAINT `fk_ArtistAlbum_Artist1` FOREIGN KEY (`Artist_ArtistID`) REFERENCES `artist` (`ArtistID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `artistalbum`
--

LOCK TABLES `artistalbum` WRITE;
/*!40000 ALTER TABLE `artistalbum` DISABLE KEYS */;
INSERT INTO `artistalbum` VALUES (1,1),(2,2),(3,3),(4,4),(5,5);
/*!40000 ALTER TABLE `artistalbum` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `artistlabel`
--

DROP TABLE IF EXISTS `artistlabel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `artistlabel` (
  `ContractStartDate` date DEFAULT NULL,
  `ContractEndDate` date DEFAULT NULL,
  `Artist_ArtistID` int NOT NULL,
  `RecordLabel_LabelID` int NOT NULL,
  PRIMARY KEY (`Artist_ArtistID`,`RecordLabel_LabelID`),
  KEY `fk_ArtistLabel_Artist1_idx` (`Artist_ArtistID`),
  KEY `fk_ArtistLabel_RecordLabel1_idx` (`RecordLabel_LabelID`),
  CONSTRAINT `fk_ArtistLabel_Artist1` FOREIGN KEY (`Artist_ArtistID`) REFERENCES `artist` (`ArtistID`),
  CONSTRAINT `fk_ArtistLabel_RecordLabel1` FOREIGN KEY (`RecordLabel_LabelID`) REFERENCES `recordlabel` (`LabelID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `artistlabel`
--

LOCK TABLES `artistlabel` WRITE;
/*!40000 ALTER TABLE `artistlabel` DISABLE KEYS */;
INSERT INTO `artistlabel` VALUES ('2020-01-01','2025-01-01',1,1),('2018-06-01','2024-06-01',2,2),('2019-03-15','2025-03-15',3,3),('2021-07-01',NULL,4,1),('2022-01-01',NULL,5,4);
/*!40000 ALTER TABLE `artistlabel` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `artistsocial`
--

DROP TABLE IF EXISTS `artistsocial`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `artistsocial` (
  `SocialID` int NOT NULL AUTO_INCREMENT,
  `Platform` varchar(50) NOT NULL,
  `URL` varchar(255) NOT NULL,
  `Artist_ArtistID` int NOT NULL,
  PRIMARY KEY (`SocialID`),
  KEY `fk_ArtistSocial_Artist1_idx` (`Artist_ArtistID`),
  CONSTRAINT `fk_ArtistSocial_Artist1` FOREIGN KEY (`Artist_ArtistID`) REFERENCES `artist` (`ArtistID`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `artistsocial`
--

LOCK TABLES `artistsocial` WRITE;
/*!40000 ALTER TABLE `artistsocial` DISABLE KEYS */;
INSERT INTO `artistsocial` VALUES (1,'Instagram','https://instagram.com/arijit',1),(2,'YouTube','https://youtube.com/arijit',1),(3,'Instagram','https://instagram.com/taylor',2),(4,'Twitter','https://twitter.com/taylor',2),(5,'Instagram','https://instagram.com/drake',3),(6,'YouTube','https://youtube.com/shreya',4),(7,'Instagram','https://instagram.com/weeknd',5);
/*!40000 ALTER TABLE `artistsocial` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `credits`
--

DROP TABLE IF EXISTS `credits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `credits` (
  `CreditID` int NOT NULL AUTO_INCREMENT,
  `PersonName` varchar(100) NOT NULL,
  `Role` varchar(50) NOT NULL,
  `EntityType` varchar(20) NOT NULL,
  `Track_TrackID` int NOT NULL,
  PRIMARY KEY (`CreditID`),
  KEY `fk_Credits_Track1_idx` (`Track_TrackID`),
  CONSTRAINT `fk_Credits_Track1` FOREIGN KEY (`Track_TrackID`) REFERENCES `track` (`TrackID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `credits`
--

LOCK TABLES `credits` WRITE;
/*!40000 ALTER TABLE `credits` DISABLE KEYS */;
/*!40000 ALTER TABLE `credits` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `linkeddevices`
--

DROP TABLE IF EXISTS `linkeddevices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `linkeddevices` (
  `DeviceID` int NOT NULL AUTO_INCREMENT,
  `DeviceType` varchar(45) NOT NULL,
  `DeviceName` varchar(45) DEFAULT NULL,
  `LastUsed` datetime DEFAULT NULL,
  `Users_UserID` int NOT NULL,
  PRIMARY KEY (`DeviceID`),
  KEY `fk_LinkedDevices_Users_idx` (`Users_UserID`),
  CONSTRAINT `fk_LinkedDevices_Users` FOREIGN KEY (`Users_UserID`) REFERENCES `users` (`UserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `linkeddevices`
--

LOCK TABLES `linkeddevices` WRITE;
/*!40000 ALTER TABLE `linkeddevices` DISABLE KEYS */;
/*!40000 ALTER TABLE `linkeddevices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notificationpreferences`
--

DROP TABLE IF EXISTS `notificationpreferences`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notificationpreferences` (
  `NotificationID` int NOT NULL AUTO_INCREMENT,
  `NotificationType` varchar(50) NOT NULL,
  `Users_UserID` int NOT NULL,
  PRIMARY KEY (`NotificationID`),
  KEY `fk_NotificationPreferences_Users1_idx` (`Users_UserID`),
  CONSTRAINT `fk_NotificationPreferences_Users1` FOREIGN KEY (`Users_UserID`) REFERENCES `users` (`UserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notificationpreferences`
--

LOCK TABLES `notificationpreferences` WRITE;
/*!40000 ALTER TABLE `notificationpreferences` DISABLE KEYS */;
/*!40000 ALTER TABLE `notificationpreferences` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payment`
--

DROP TABLE IF EXISTS `payment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment` (
  `PaymentID` int NOT NULL AUTO_INCREMENT,
  `Amount` decimal(10,2) NOT NULL,
  `Currency` varchar(10) NOT NULL,
  `Status` varchar(20) NOT NULL,
  `TransactionDate` datetime NOT NULL,
  `GatewayReferenceID` varchar(100) DEFAULT NULL,
  `PaymentMethod` varchar(50) DEFAULT NULL,
  `Subscription_SubscriptionID` int NOT NULL,
  PRIMARY KEY (`PaymentID`),
  KEY `fk_Payment_Subscription1_idx` (`Subscription_SubscriptionID`),
  CONSTRAINT `fk_Payment_Subscription1` FOREIGN KEY (`Subscription_SubscriptionID`) REFERENCES `subscription` (`SubscriptionID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment`
--

LOCK TABLES `payment` WRITE;
/*!40000 ALTER TABLE `payment` DISABLE KEYS */;
/*!40000 ALTER TABLE `payment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `plan`
--

DROP TABLE IF EXISTS `plan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `plan` (
  `PlanID` int NOT NULL AUTO_INCREMENT,
  `PlanName` varchar(50) NOT NULL,
  `Price` decimal(10,2) NOT NULL,
  `Currency` varchar(50) NOT NULL,
  `Features` longtext,
  `MaxDevices` int DEFAULT NULL,
  PRIMARY KEY (`PlanID`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `plan`
--

LOCK TABLES `plan` WRITE;
/*!40000 ALTER TABLE `plan` DISABLE KEYS */;
INSERT INTO `plan` VALUES (1,'Free',0.00,'USD','Basic streaming with ads',1),(2,'Premium Mini',49.00,'INR','Ad-free music, limited skips',1),(3,'Premium Individual',119.00,'INR','Ad-free, offline download, unlimited skips',1),(4,'Premium Duo',149.00,'INR','2 accounts, ad-free, offline download',2),(5,'Premium Family',179.00,'INR','Up to 6 accounts, parental controls',6);
/*!40000 ALTER TABLE `plan` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `playlist`
--

DROP TABLE IF EXISTS `playlist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `playlist` (
  `PlaylistID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) NOT NULL,
  `Description` longtext,
  `CreatedAt` datetime NOT NULL,
  `IsPublic` tinyint(1) NOT NULL,
  `IsCollaborative` tinyint(1) DEFAULT NULL,
  `Users_UserID` int NOT NULL,
  PRIMARY KEY (`PlaylistID`),
  KEY `fk_Playlist_Users1_idx` (`Users_UserID`),
  CONSTRAINT `fk_Playlist_Users1` FOREIGN KEY (`Users_UserID`) REFERENCES `users` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `playlist`
--

LOCK TABLES `playlist` WRITE;
/*!40000 ALTER TABLE `playlist` DISABLE KEYS */;
INSERT INTO `playlist` VALUES (1,'Chill Vibes','Relaxing songs','2026-04-06 01:03:30',1,0,1),(2,'Workout Mix','High energy songs','2026-04-06 01:03:30',1,0,2),(3,'Romantic Hits','Love songs collection','2026-04-06 01:03:30',1,1,3),(4,'Party Playlist','Dance and party songs','2026-04-06 01:03:30',1,0,4),(5,'Late Night','Soft and calm music','2026-04-06 01:03:30',0,0,5);
/*!40000 ALTER TABLE `playlist` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `playlisttrack`
--

DROP TABLE IF EXISTS `playlisttrack`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `playlisttrack` (
  `AddedAt` datetime DEFAULT NULL,
  `Playlist_PlaylistID` int NOT NULL,
  `Track_TrackID` int NOT NULL,
  PRIMARY KEY (`Playlist_PlaylistID`,`Track_TrackID`),
  KEY `fk_PlaylistTrack_Playlist1_idx` (`Playlist_PlaylistID`),
  KEY `fk_PlaylistTrack_Track1_idx` (`Track_TrackID`),
  CONSTRAINT `fk_PlaylistTrack_Playlist1` FOREIGN KEY (`Playlist_PlaylistID`) REFERENCES `playlist` (`PlaylistID`),
  CONSTRAINT `fk_PlaylistTrack_Track1` FOREIGN KEY (`Track_TrackID`) REFERENCES `track` (`TrackID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `playlisttrack`
--

LOCK TABLES `playlisttrack` WRITE;
/*!40000 ALTER TABLE `playlisttrack` DISABLE KEYS */;
INSERT INTO `playlisttrack` VALUES ('2026-04-06 01:04:55',1,1),('2026-04-06 01:04:55',1,5),('2026-04-06 01:04:55',2,3),('2026-04-06 01:04:55',2,5),('2026-04-06 01:04:55',3,1),('2026-04-06 01:04:55',4,3),('2026-04-06 01:04:55',4,5),('2026-04-06 01:04:55',5,2);
/*!40000 ALTER TABLE `playlisttrack` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recordlabel`
--

DROP TABLE IF EXISTS `recordlabel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recordlabel` (
  `LabelID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) NOT NULL,
  `Website` varchar(255) DEFAULT NULL,
  `Country` varchar(50) DEFAULT NULL,
  `Verified` tinyint(1) NOT NULL,
  `ContactEmail` varchar(100) DEFAULT NULL,
  `ContactPhone` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`LabelID`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recordlabel`
--

LOCK TABLES `recordlabel` WRITE;
/*!40000 ALTER TABLE `recordlabel` DISABLE KEYS */;
INSERT INTO `recordlabel` VALUES (1,'T-Series','https://tseries.com','India',1,'contact@tseries.com','1111111111'),(2,'Sony Music','https://sonymusic.com','USA',1,'info@sonymusic.com','2222222222'),(3,'Universal Music','https://universalmusic.com','USA',1,'support@umusic.com','3333333333'),(4,'Warner Music','https://warnermusic.com','USA',1,'hello@warner.com','4444444444');
/*!40000 ALTER TABLE `recordlabel` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `royalty`
--

DROP TABLE IF EXISTS `royalty`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `royalty` (
  `RoyaltyID` int NOT NULL AUTO_INCREMENT,
  `TotalAmount` decimal(10,2) NOT NULL,
  `StreamCount` int DEFAULT NULL,
  `Currency` varchar(10) NOT NULL,
  `PaymentStatus` varchar(20) NOT NULL,
  `DisbursedAt` datetime DEFAULT NULL,
  `PeriodStart` date NOT NULL,
  `PeriodEnd` date NOT NULL,
  `RoyaltyRate` decimal(10,4) DEFAULT NULL,
  `Artist_ArtistID` int NOT NULL,
  `Track_TrackID` int NOT NULL,
  PRIMARY KEY (`RoyaltyID`),
  KEY `fk_Royalty_Artist1_idx` (`Artist_ArtistID`),
  KEY `fk_Royalty_Track1_idx` (`Track_TrackID`),
  CONSTRAINT `fk_Royalty_Artist1` FOREIGN KEY (`Artist_ArtistID`) REFERENCES `artist` (`ArtistID`),
  CONSTRAINT `fk_Royalty_Track1` FOREIGN KEY (`Track_TrackID`) REFERENCES `track` (`TrackID`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `royalty`
--

LOCK TABLES `royalty` WRITE;
/*!40000 ALTER TABLE `royalty` DISABLE KEYS */;
INSERT INTO `royalty` VALUES (1,5000.00,10000,'INR','Paid','2026-04-06 01:08:15','2024-01-01','2024-01-31',0.5000,1,1),(2,8000.00,15000,'USD','Paid','2026-04-06 01:08:15','2024-01-01','2024-01-31',0.5300,2,2),(3,6000.00,12000,'USD','Pending',NULL,'2024-01-01','2024-01-31',0.5000,3,3),(4,4000.00,9000,'INR','Paid','2026-04-06 01:08:15','2024-01-01','2024-01-31',0.4400,4,4),(5,9000.00,20000,'USD','Pending',NULL,'2024-01-01','2024-01-31',0.4500,5,5);
/*!40000 ALTER TABLE `royalty` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `show`
--

DROP TABLE IF EXISTS `show`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `show` (
  `ShowID` int NOT NULL AUTO_INCREMENT,
  `Title` varchar(100) NOT NULL,
  `Description` longtext,
  `ShowDate` date NOT NULL,
  `ShowTime` time NOT NULL,
  `VenuName` varchar(100) DEFAULT NULL,
  `VenueCity` varchar(50) DEFAULT NULL,
  `VenueCountry` varchar(50) DEFAULT NULL,
  `Status` varchar(20) DEFAULT NULL,
  `Artist_ArtistID` int NOT NULL,
  PRIMARY KEY (`ShowID`),
  KEY `fk_Show_Artist1_idx` (`Artist_ArtistID`),
  CONSTRAINT `fk_Show_Artist1` FOREIGN KEY (`Artist_ArtistID`) REFERENCES `artist` (`ArtistID`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `show`
--

LOCK TABLES `show` WRITE;
/*!40000 ALTER TABLE `show` DISABLE KEYS */;
INSERT INTO `show` VALUES (1,'Arijit Live Mumbai','Live concert in Mumbai','2024-06-10','19:00:00','NSCI Dome','Mumbai','India','Scheduled',1),(2,'Taylor Swift Eras Tour','Global tour performance','2024-07-15','20:00:00','Madison Square Garden','New York','USA','Scheduled',2),(3,'Drake Live Toronto','Rap concert','2024-08-05','21:00:00','Scotiabank Arena','Toronto','Canada','Scheduled',3),(4,'Shreya Classical Night','Classical music show','2024-06-25','18:30:00','Royal Opera House','Mumbai','India','Scheduled',4),(5,'Weeknd After Hours Tour','Live performance tour','2024-09-01','20:30:00','Staples Center','Los Angeles','USA','Scheduled',5);
/*!40000 ALTER TABLE `show` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `streamlog`
--

DROP TABLE IF EXISTS `streamlog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `streamlog` (
  `StreamID` int NOT NULL AUTO_INCREMENT,
  `StartTime` datetime NOT NULL,
  `EndTime` datetime DEFAULT NULL,
  `StreamDuration` int DEFAULT NULL,
  `WasCompleted` tinyint(1) DEFAULT NULL,
  `SkippedAt` int DEFAULT NULL,
  `DeviceType` varchar(50) DEFAULT NULL,
  `Country` varchar(50) DEFAULT NULL,
  `Users_UserID` int NOT NULL,
  `Track_TrackID` int NOT NULL,
  PRIMARY KEY (`StreamID`),
  KEY `fk_StreamLog_Users1_idx` (`Users_UserID`),
  KEY `fk_StreamLog_Track1_idx` (`Track_TrackID`),
  CONSTRAINT `fk_StreamLog_Track1` FOREIGN KEY (`Track_TrackID`) REFERENCES `track` (`TrackID`),
  CONSTRAINT `fk_StreamLog_Users1` FOREIGN KEY (`Users_UserID`) REFERENCES `users` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `streamlog`
--

LOCK TABLES `streamlog` WRITE;
/*!40000 ALTER TABLE `streamlog` DISABLE KEYS */;
INSERT INTO `streamlog` VALUES (1,'2026-04-06 01:06:47','2026-04-06 01:10:47',240,1,NULL,'Mobile','India',1,1),(2,'2026-04-06 01:06:47','2026-04-06 01:09:47',180,1,NULL,'Laptop','USA',2,2),(3,'2026-04-06 01:06:47','2026-04-06 01:08:47',120,0,60,'Mobile','India',3,3),(4,'2026-04-06 01:06:47','2026-04-06 01:11:47',300,1,NULL,'Tablet','UAE',4,4),(5,'2026-04-06 01:06:47','2026-04-06 01:09:47',200,1,NULL,'Mobile','USA',5,5),(6,'2026-04-06 01:06:47','2026-04-06 01:08:47',150,0,30,'Laptop','India',1,6);
/*!40000 ALTER TABLE `streamlog` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = cp850 */ ;
/*!50003 SET character_set_results = cp850 */ ;
/*!50003 SET collation_connection  = cp850_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_stream_insert` AFTER INSERT ON `streamlog` FOR EACH ROW BEGIN
    UPDATE royalty
    SET StreamCount = StreamCount + 1
    WHERE Track_TrackID = NEW.Track_TrackID;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `subscription`
--

DROP TABLE IF EXISTS `subscription`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subscription` (
  `SubscriptionID` int NOT NULL AUTO_INCREMENT,
  `StartDate` datetime NOT NULL,
  `EndDate` datetime DEFAULT NULL,
  `AutoRenewal` tinyint(1) NOT NULL,
  `Status` varchar(20) NOT NULL,
  `NextBillingDate` datetime DEFAULT NULL,
  `Plan_PlanID` int NOT NULL,
  `Users_UserID` int NOT NULL,
  PRIMARY KEY (`SubscriptionID`),
  UNIQUE KEY `Users_UserID_UNIQUE` (`Users_UserID`),
  KEY `fk_Subscription_Plan1_idx` (`Plan_PlanID`),
  KEY `fk_Subscription_Users1_idx` (`Users_UserID`),
  CONSTRAINT `fk_Subscription_Plan1` FOREIGN KEY (`Plan_PlanID`) REFERENCES `plan` (`PlanID`),
  CONSTRAINT `fk_Subscription_Users1` FOREIGN KEY (`Users_UserID`) REFERENCES `users` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subscription`
--

LOCK TABLES `subscription` WRITE;
/*!40000 ALTER TABLE `subscription` DISABLE KEYS */;
INSERT INTO `subscription` VALUES (1,'2026-04-06 00:35:17','2026-05-06 00:35:17',1,'Active','2026-05-06 00:35:17',2,1),(2,'2026-04-06 00:35:17','2026-05-06 00:35:17',1,'Active','2026-05-06 00:35:17',3,2),(3,'2026-04-06 00:35:17','2026-05-06 00:35:17',0,'Active','2026-05-06 00:35:17',1,3),(4,'2026-04-06 00:35:17','2026-05-06 00:35:17',1,'Active','2026-05-06 00:35:17',4,4),(5,'2026-04-06 00:35:17','2026-05-06 00:35:17',1,'Active','2026-05-06 00:35:17',5,5);
/*!40000 ALTER TABLE `subscription` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tag`
--

DROP TABLE IF EXISTS `tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tag` (
  `TagID` int NOT NULL AUTO_INCREMENT,
  `TagName` varchar(50) NOT NULL,
  PRIMARY KEY (`TagID`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tag`
--

LOCK TABLES `tag` WRITE;
/*!40000 ALTER TABLE `tag` DISABLE KEYS */;
INSERT INTO `tag` VALUES (1,'Romantic'),(2,'Pop'),(3,'Hip-Hop'),(4,'Classical'),(5,'Party');
/*!40000 ALTER TABLE `tag` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ticket`
--

DROP TABLE IF EXISTS `ticket`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ticket` (
  `TicketID` int NOT NULL AUTO_INCREMENT,
  `Price` decimal(10,2) NOT NULL,
  `PurchaseDate` datetime NOT NULL,
  `Status` varchar(20) DEFAULT NULL,
  `SeatSection` varchar(20) DEFAULT NULL,
  `SeatRow` varchar(20) DEFAULT NULL,
  `SeatNumber` varchar(20) DEFAULT NULL,
  `SeatCategory` varchar(50) DEFAULT NULL,
  `Show_ShowID` int NOT NULL,
  `Users_UserID` int NOT NULL,
  PRIMARY KEY (`TicketID`),
  KEY `fk_Ticket_Show1_idx` (`Show_ShowID`),
  KEY `fk_Ticket_Users1_idx` (`Users_UserID`),
  CONSTRAINT `fk_Ticket_Show1` FOREIGN KEY (`Show_ShowID`) REFERENCES `show` (`ShowID`),
  CONSTRAINT `fk_Ticket_Users1` FOREIGN KEY (`Users_UserID`) REFERENCES `users` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ticket`
--

LOCK TABLES `ticket` WRITE;
/*!40000 ALTER TABLE `ticket` DISABLE KEYS */;
INSERT INTO `ticket` VALUES (1,1500.00,'2026-04-06 01:18:41','Booked','A','1','10','VIP',1,1),(2,200.00,'2026-04-06 01:18:41','Booked','B','3','25','Standard',2,2),(3,250.00,'2026-04-06 01:18:41','Booked','C','5','40','Standard',3,3),(4,1800.00,'2026-04-06 01:18:41','Booked','A','2','15','VIP',4,4),(5,300.00,'2026-04-06 01:18:41','Booked','D','6','50','Economy',5,5);
/*!40000 ALTER TABLE `ticket` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = cp850 */ ;
/*!50003 SET character_set_results = cp850 */ ;
/*!50003 SET collation_connection  = cp850_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `prevent_duplicate_seat_booking` BEFORE INSERT ON `ticket` FOR EACH ROW BEGIN
    IF EXISTS (
        SELECT 1 
        FROM ticket
        WHERE Show_ShowID = NEW.Show_ShowID
        AND SeatSection = NEW.SeatSection
        AND SeatRow = NEW.SeatRow
        AND SeatNumber = NEW.SeatNumber
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Seat already booked for this show';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `track`
--

DROP TABLE IF EXISTS `track`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `track` (
  `TrackID` int NOT NULL AUTO_INCREMENT,
  `Title` varchar(100) NOT NULL,
  `Duration` int DEFAULT NULL,
  `Language` varchar(50) DEFAULT NULL,
  `Lyrics` longtext,
  `ReleaseDate` date DEFAULT NULL,
  `BPM` int DEFAULT NULL,
  `Album_AlbumID` int DEFAULT NULL,
  PRIMARY KEY (`TrackID`),
  KEY `fk_Track_Album1_idx` (`Album_AlbumID`),
  CONSTRAINT `fk_Track_Album1` FOREIGN KEY (`Album_AlbumID`) REFERENCES `album` (`AlbumID`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `track`
--

LOCK TABLES `track` WRITE;
/*!40000 ALTER TABLE `track` DISABLE KEYS */;
INSERT INTO `track` VALUES (1,'Tum Hi Ho',270,'Hindi','Lyrics...','2013-04-26',90,1),(2,'Blank Space',230,'English','Lyrics...','2014-10-27',96,2),(3,'God?s Plan',198,'English','Lyrics...','2018-01-19',77,3),(4,'Dola Re Dola',300,'Hindi','Lyrics...','2002-07-12',85,4),(5,'Blinding Lights',200,'English','Lyrics...','2019-11-29',171,5),(6,'Independent Single',180,'English','Lyrics...','2023-01-01',100,NULL);
/*!40000 ALTER TABLE `track` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tracktag`
--

DROP TABLE IF EXISTS `tracktag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tracktag` (
  `Track_TrackID` int NOT NULL,
  `Tag_TagID` int NOT NULL,
  PRIMARY KEY (`Track_TrackID`,`Tag_TagID`),
  KEY `fk_TrackTag_Track1_idx` (`Track_TrackID`),
  KEY `fk_TrackTag_Tag1_idx` (`Tag_TagID`),
  CONSTRAINT `fk_TrackTag_Tag1` FOREIGN KEY (`Tag_TagID`) REFERENCES `tag` (`TagID`),
  CONSTRAINT `fk_TrackTag_Track1` FOREIGN KEY (`Track_TrackID`) REFERENCES `track` (`TrackID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tracktag`
--

LOCK TABLES `tracktag` WRITE;
/*!40000 ALTER TABLE `tracktag` DISABLE KEYS */;
INSERT INTO `tracktag` VALUES (1,1),(2,2),(3,3),(4,4),(5,5),(6,2);
/*!40000 ALTER TABLE `tracktag` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `UserID` int NOT NULL AUTO_INCREMENT,
  `FirstName` varchar(50) NOT NULL,
  `Last_Name` varchar(50) NOT NULL,
  `Username` varchar(50) NOT NULL,
  `Language` varchar(45) NOT NULL,
  `Language_Pref` varchar(45) DEFAULT NULL,
  `Email` varchar(100) NOT NULL,
  `PasswordHash` varchar(255) NOT NULL,
  `AccountStatus` enum('Active','Suspended','Deactivated','Deleted') NOT NULL DEFAULT 'Active',
  `CreatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `ProfileImage` varchar(255) DEFAULT NULL,
  `LastLogin` timestamp NOT NULL,
  `DOB` date NOT NULL,
  `Country` varchar(50) NOT NULL,
  PRIMARY KEY (`UserID`),
  UNIQUE KEY `User_name_UNIQUE` (`Username`),
  UNIQUE KEY `Email_id_UNIQUE` (`Email`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Riya','Sharma','riya_s','English','Hindi','riya@gmail.com','hash123','Active','2026-04-06 00:26:32','img1.jpg','2026-04-05 18:56:32','2003-05-12','India'),(2,'Aman','Verma','aman_v','English','English','aman@gmail.com','hash456','Active','2026-04-06 00:26:32','img2.jpg','2026-04-05 18:56:32','2002-08-21','India'),(3,'Sara','Khan','sara_k','English','Urdu','sara@gmail.com','hash789','Active','2026-04-06 00:26:32','img3.jpg','2026-04-05 18:56:32','2001-11-30','UAE'),(4,'Emily','Johnson','emily_j','English','English','emily@gmail.com','hash321','Active','2026-04-06 00:26:32','img4.jpg','2026-04-05 18:56:32','1999-03-15','USA'),(5,'Michael','Brown','mike_b','English','English','mike@gmail.com','hash654','Active','2026-04-06 00:26:32','img5.jpg','2026-04-05 18:56:32','1998-07-09','USA');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-14 16:52:40
