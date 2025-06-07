CREATE DATABASE IF NOT EXISTS ufc;
USE ufc;

-- insert order 1
CREATE TABLE IF NOT EXISTS stances (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    stance VARCHAR(50)
);

-- insert order 2
CREATE TABLE IF NOT EXISTS fighters (
    id VARCHAR(16) UNIQUE NOT NULL PRIMARY KEY,
    fighter_name VARCHAR(100),
    height FLOAT DEFAULT NULL,
    weight INT DEFAULT NULL,
    reach FLOAT DEFAULT NULL,
    stance_id INT DEFAULT NULL,
    date_of_birth DATE DEFAULT NULL,
    significant_strikes_per_minute FLOAT DEFAULT NULL,
    striking_accuracy_per FLOAT DEFAULT NULL,
    strikes_absorbed_per_minute FLOAT DEFAULT NULL,
    strike_defence_per FLOAT DEFAULT NULL,
    average_takedowns_per_15_minutes FLOAT DEFAULT NULL,
    takedown_accuracy_per FLOAT DEFAULT NULL,
    takedown_defence_per FLOAT DEFAULT NULL,
    average_submission_attempts_per_15_min FLOAT DEFAULT NULL,
    wins INT,
    losses INT,
    draws INT,
    FOREIGN KEY(stance_id) REFERENCES stances(id)
);

-- insert order 3
CREATE TABLE IF NOT EXISTS cities (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(100)
);
-- insert order 4
CREATE TABLE IF NOT EXISTS states (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    state VARCHAR(100)
);
-- insert order 5
CREATE TABLE IF NOT EXISTS countries (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    state VARCHAR(100)
);
-- has nulls in state_id
-- insert order 6
CREATE TABLE IF NOT EXISTS events (
    id VARCHAR(16) UNIQUE NOT NULL PRIMARY KEY,
    event_name VARCHAR(255),
    event_date DATE,
    city_id INT DEFAULT NULL,
    state_id INT DEFAULT NULL,
    country_id INT DEFAULT NULL,
    FOREIGN KEY(city_id) REFERENCES cities(id),
    FOREIGN KEY(state_id) REFERENCES states(id),
    FOREIGN KEY(country_id) REFERENCES countries(id)
);
-- insert order 7
CREATE TABLE IF NOT EXISTS weight_classes (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    class VARCHAR(50)
);
-- insert order 8
CREATE TABLE IF NOT EXISTS methods (
 id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
 method VARCHAR(50)
);
-- insert order 9
CREATE TABLE IF NOT EXISTS fights (
    id VARCHAR(16) UNIQUE NOT NULL PRIMARY KEY,
    event_id VARCHAR(16),
    fighter_1_id VARCHAR(16),
    fighter_2_id VARCHAR(16),
    weight_class_id INT DEFAULT NULL,
    method_id INT DEFAULT NULL,
    FOREIGN KEY (weight_class_id) REFERENCES weight_classes(id),
    FOREIGN KEY (method_id) REFERENCES methods(id),
    FOREIGN KEY (event_id) REFERENCES events(id),
    FOREIGN KEY (fighter_1_id) REFERENCES fighters(id),
    FOREIGN KEY (fighter_2_id) REFERENCES fighters(id)
);

-- insert order 10
CREATE TABLE IF NOT EXISTS fight_stats (
    fight_id VARCHAR(16) UNIQUE NOT NULL PRIMARY KEY,
    fighter_1_alias VARCHAR(100),
    fighter_2_alias VARCHAR(100),
    fighter_1_fight_conclusion CHAR(10),
    fighter_2_fight_conclusion CHAR(10),
    fighter_1_knockdowns INT,
    fighter_2_knockdowns INT,
    fighter_1_significant_strikes_per FLOAT,
    fighter_2_significant_strikes_per FLOAT,
    fighter_1_takedowns_per FLOAT,
    fighter_2_takedowns_per FLOAT,
    fighter_1_submission_attempts FLOAT,
    fighter_2_submission_attempts FLOAT,
    fighter_1_reversals FLOAT,
    fighter_2_reversals FLOAT,
    fighter_1_strikes_landed INT,
    fighter_1_strikes_attempted INT,
    fighter_2_strikes_landed INT,
    fighter_2_strikes_attempted INT,
    FOREIGN KEY (fight_id) REFERENCES fights(id)
);

