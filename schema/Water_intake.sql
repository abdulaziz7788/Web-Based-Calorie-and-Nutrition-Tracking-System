CREATE TABLE Water_intake(
	water_id int primary key auto_increment,
    user_id int NOT NULL,
    amount FLOAT NOT NULL DEFAULT 0 CHECK(amount >= 0),
    unit ENUM('ML', 'LITER', 'CUP') DEFAULT 'ML',
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

	FOREIGN KEY(user_id) REFERENCES User(user_id)
		ON DELETE CASCADE

);