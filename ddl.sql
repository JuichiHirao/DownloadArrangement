DROP TABLE akb48;
CREATE TABLE akb48 (
  id MEDIUMINT NOT NULL AUTO_INCREMENT,
  group_name VARCHAR(255),
  title TEXT,
  subtitle TEXT,
  member TEXT,
  the_date DATETIME,
  memo TEXT,
  memo2 TEXT,
  remark TEXT,
  filename TEXT,
  rating1 INT DEFAULT 0,
  rating2 INT DEFAULT 0,
  status ENUM('exist', 'not exist'),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);
