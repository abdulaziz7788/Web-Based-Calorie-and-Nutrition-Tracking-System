CREATE TABLE Workout_type(
	workout_type_id int primary key auto_increment,
    type_name varchar(100)NOT NULL UNIQUE
    
    );

CREATE TABLE Workout_log(
	workout_id int primary key AUTO_INCREMENT,
    user_id int NOT NULL,
    workout_type_id int NOT NULL,
    duration_minutes FLOAT CHECK(duration_minutes > 0),
    calories_burned FLOAT CHECK(calories_burned > 0),
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id)REFERENCES User(user_id)
		ON DELETE CASCADE ,
	FOREIGN KEY(workout_type_id)REFERENCES Workout_type(workout_type_id)
		ON DELETE CASCADE 
    
	);
    
CREATE TABLE Exercise_library(
	exercise_id int primary key auto_increment,
	workout_type_id int NOT NULL,
    exercise_name varchar(150) NOT NULL,
    ex_description Text,
    calories_per_minute FLOAT CHECK(calories_per_minute > 0),
    difficulty ENUM('EASY','MEDIUM','HARD'),
	muscle_group ENUM(
			'CHEST','BACK','SHOULDERS','ARMS',
			'LEGS','CORE','FULL_BODY'
		) NOT NULL,
    UNIQUE(exercise_name,workout_type_id),
    FOREIGN KEY(workout_type_id)REFERENCES Workout_type(workout_type_id)
		ON DELETE CASCADE 


);