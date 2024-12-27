Create table shop(
	id int auto_increment primary key,
	customers_entering int not null,
    customers_exiting int not null,
    `time` time not null,
    `date` date not null
)