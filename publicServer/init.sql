
DROP TABLE IF EXISTS `ssh_tunnel_params`;
CREATE TABLE `ssh_tunnel_params` (
	`id` BIGINT(20) NOT NULL AUTO_INCREMENT,
	`customer_serial` VARCHAR(80) NOT NULL DEFAULT '',
    `random_password` VARCHAR(30) NOT NULL DEFAULT '', -- customer random password
    `public_port` INT(11) NOT NULL DEFAULT '0', -- proxy server public port	
	`source_port` INT(11) NOT NULL DEFAULT '0', -- customer port
	`tunnel_type` INT(11) NOT NULL DEFAULT '0', -- 1 : ssh, 2 : http 
	`mod_timestamp` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
;

COMMIT;
