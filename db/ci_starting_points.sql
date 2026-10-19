-- Disposable development-only initial point allocation for Trojan level 1.
-- The original COPS Database::createPlayer must query this table successfully.
CREATE TABLE `point_allot` (
  `profession` TINYINT UNSIGNED NOT NULL,
  `level` TINYINT UNSIGNED NOT NULL,
  `force` SMALLINT UNSIGNED NOT NULL,
  `speed` SMALLINT UNSIGNED NOT NULL,
  `health` SMALLINT UNSIGNED NOT NULL,
  `soul` SMALLINT UNSIGNED NOT NULL,
  PRIMARY KEY (`profession`, `level`)
) ENGINE=InnoDB;
INSERT INTO `point_allot`
(`profession`,`level`,`force`,`speed`,`health`,`soul`)
VALUES (1,1,4,5,6,7);
