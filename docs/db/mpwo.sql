CREATE DATABASE IF NOT EXISTS mpwo  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE mpwo;

CREATE TABLE users ( 
id int(4) UNSIGNED NOT NULL AUTO_INCREMENT, 
username varchar(20) NOT NULL,
pwd varchar(64) NOT NULL,
first_name varchar(50) NOT NULL,
last_name varchar(50) NOT NULL,
birthday date,
photo BLOB,
PRIMARY KEY (id) 
) ENGINE=InnoDB;

CREATE TABLE sports ( 
id int(4) UNSIGNED NOT NULL AUTO_INCREMENT, 
label varchar(50) NOT NULL,
PRIMARY KEY (id) 
) ENGINE=InnoDB;

CREATE TABLE gpx ( 
id int(4) UNSIGNED NOT NULL AUTO_INCREMENT, 
file BLOB NOT NULL,
PRIMARY KEY (id) 
) ENGINE=InnoDB;

CREATE TABLE activities ( 
id int(4) UNSIGNED NOT NULL AUTO_INCREMENT, 
user_id int(4) UNSIGNED NOT NULL,
sport_id int(4) UNSIGNED NOT NULL,
gpx_id int(4),
activity_date datetime NOT NULL,
duration int(4) NOT NULL,
pauses int(4),
distance int(4),
min_alt int(4),
max_alt int(4),
descent int(4),
ascent int(4),
max_speed int(4),
ave_speed int(4),
PRIMARY KEY (id),
FOREIGN KEY (user_id)
    REFERENCES users(id),
FOREIGN KEY (sport_id)
    REFERENCES sports(id)
) ENGINE=InnoDB;

CREATE TABLE personalRecords ( 
id int(4) UNSIGNED NOT NULL AUTO_INCREMENT, 
activity_id int(4) UNSIGNED NOT NULL,
record_type varchar(50) NOT NULL,
value int(4),
PRIMARY KEY (id),
FOREIGN KEY (activity_id)
    REFERENCES activities(id)
) ENGINE=InnoDB;