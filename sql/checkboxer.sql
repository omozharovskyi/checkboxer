-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: mysql
-- Generation Time: Jan 28, 2023 at 08:33 PM
-- Server version: 8.0.32
-- PHP Version: 8.0.19

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `checkboxer`
--

-- --------------------------------------------------------

--
-- Table structure for table `orders_list`
--

CREATE TABLE `orders_list` (
  `id` int UNSIGNED NOT NULL COMMENT 'internal db ID',
  `internal_order_status` enum('unconfirmed','confirmed','ignored') NOT NULL DEFAULT 'unconfirmed',
  `create_date` datetime NOT NULL COMMENT 'date when order was placed',
  `order_id` bigint NOT NULL COMMENT 'order ID in prom.ua',
  `order_sum` float(8,2) NOT NULL DEFAULT '0.00' COMMENT 'order sum to pay',
  `payed_sum` float(8,2) NOT NULL DEFAULT '0.00' COMMENT 'payed for order',
  `link_to_check` varchar(250) NOT NULL COMMENT 'created link to check'
) ENGINE=InnoDB DEFAULT CHARSET=utf32;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `orders_list`
--
ALTER TABLE `orders_list`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `order_id_unq_index` (`order_id`),
  ADD KEY `creation_date_index` (`create_date`),
  ADD KEY `internal_order_status_index` (`internal_order_status`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `orders_list`
--
ALTER TABLE `orders_list`
  MODIFY `id` int UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'internal db ID';
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
