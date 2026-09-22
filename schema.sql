CREATE DATABASE IF NOT EXISTS research_portal;
USE research_portal;

-- one table is enough for this project
CREATE TABLE IF NOT EXISTS opportunities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    research_area VARCHAR(100) NOT NULL,
    faculty_name VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    required_skills VARCHAR(255) NOT NULL,
    positions INT NOT NULL,
    deadline DATE NOT NULL,
    status VARCHAR(10) NOT NULL DEFAULT 'Open'
);
