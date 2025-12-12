CREATE TABLE sleep_log (
    sleep_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    hours DECIMAL(4,2),
    sleep_date DATE NOT NULL,

    FOREIGN KEY (user_id) REFERENCES user(user_id)
    ON DELETE CASCADE
);
