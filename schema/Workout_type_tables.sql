CREATE TABLE Workout_type(
    workout_type_id INT PRIMARY KEY AUTO_INCREMENT,
    type_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE Workout_log(
    workout_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    workout_type_id INT NOT NULL,

    duration_minutes INT CHECK(duration_minutes > 0),
    calories_burned FLOAT CHECK(calories_burned >= 0),

    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id) REFERENCES User(user_id)
        ON DELETE CASCADE,

    FOREIGN KEY(workout_type_id) REFERENCES Workout_type(workout_type_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_workout_user ON Workout_log(user_id, logged_at);

CREATE TABLE Exercise_library(
    exercise_id INT PRIMARY KEY AUTO_INCREMENT,
    workout_type_id INT NOT NULL,

    exercise_name VARCHAR(150) NOT NULL,
    ex_description TEXT,

    calories_per_minute FLOAT CHECK(calories_per_minute >= 0),

    difficulty ENUM('EASY', 'MEDIUM', 'HARD'),

    muscle_group ENUM(
        'CHEST', 'BACK', 'SHOULDERS', 'ARMS',
        'LEGS', 'CORE', 'FULL_BODY'
    ) NOT NULL,

    UNIQUE (exercise_name, workout_type_id),

    FOREIGN KEY(workout_type_id) REFERENCES Workout_type(workout_type_id)
        ON DELETE CASCADE
);


