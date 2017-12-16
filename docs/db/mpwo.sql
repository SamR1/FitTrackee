CREATE DATABASE IF NOT EXISTS mpwo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS mpwo_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'mpwo'@'localhost' IDENTIFIED BY 'mpwo';
GRANT ALL PRIVILEGES ON `mpwo` . * TO 'mpwo'@'localhost';
GRANT ALL PRIVILEGES ON `mpwo_dev` . * TO 'mpwo'@'localhost';
FLUSH PRIVILEGES;