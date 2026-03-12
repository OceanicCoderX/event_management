-- College Event & Talent Show Management System
-- Database: event_management_db

CREATE DATABASE IF NOT EXISTS event_management_db;
USE event_management_db;

-- Drop tables if they exist
DROP TABLE IF EXISTS results;
DROP TABLE IF EXISTS votes;
DROP TABLE IF EXISTS scores;
DROP TABLE IF EXISTS criteria;
DROP TABLE IF EXISTS judge_assignments;
DROP TABLE IF EXISTS participants;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;

-- 1. USERS
CREATE TABLE users (
  user_id INT PRIMARY KEY AUTO_INCREMENT,
  full_name VARCHAR(100) NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  phone VARCHAR(15),
  password VARCHAR(255) NOT NULL,
  role ENUM('student','participant','judge','admin') NOT NULL,
  photo VARCHAR(255),
  bio TEXT,
  created_at DATETIME DEFAULT NOW()
);

-- 2. CATEGORIES
CREATE TABLE categories (
  category_id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  icon VARCHAR(50)
);

-- 3. EVENTS
CREATE TABLE events (
  event_id INT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(200) NOT NULL,
  category_id INT,
  description TEXT,
  venue VARCHAR(200),
  event_date DATE NOT NULL,
  registration_deadline DATE,
  status ENUM('Upcoming','Ongoing','Completed','Cancelled') DEFAULT 'Upcoming',
  voting_open TINYINT(1) DEFAULT 0,
  scores_locked TINYINT(1) DEFAULT 0,
  results_announced TINYINT(1) DEFAULT 0,
  judge_weight DECIMAL(5,2) DEFAULT 60.00,
  vote_weight DECIMAL(5,2) DEFAULT 40.00,
  created_at DATETIME DEFAULT NOW(),
  FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

-- 4. PARTICIPANTS
CREATE TABLE participants (
  participant_id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  event_id INT,
  performance_title VARCHAR(200),
  category_entry VARCHAR(100),
  status ENUM('Pending','Approved','Rejected') DEFAULT 'Pending',
  registered_at DATETIME DEFAULT NOW(),
  FOREIGN KEY (user_id) REFERENCES users(user_id),
  FOREIGN KEY (event_id) REFERENCES events(event_id)
);

-- 5. JUDGE ASSIGNMENTS
CREATE TABLE judge_assignments (
  assignment_id INT PRIMARY KEY AUTO_INCREMENT,
  judge_user_id INT,
  event_id INT,
  assigned_at DATETIME DEFAULT NOW(),
  UNIQUE KEY unique_judge_event (judge_user_id, event_id),
  FOREIGN KEY (judge_user_id) REFERENCES users(user_id),
  FOREIGN KEY (event_id) REFERENCES events(event_id)
);

-- 6. CRITERIA
CREATE TABLE criteria (
  criteria_id INT PRIMARY KEY AUTO_INCREMENT,
  event_id INT,
  criteria_name VARCHAR(100) NOT NULL,
  max_marks INT NOT NULL DEFAULT 10,
  description VARCHAR(200),
  FOREIGN KEY (event_id) REFERENCES events(event_id)
);

-- 7. SCORES
CREATE TABLE scores (
  score_id INT PRIMARY KEY AUTO_INCREMENT,
  judge_user_id INT,
  participant_id INT,
  criteria_id INT,
  marks DECIMAL(5,2) NOT NULL,
  scored_at DATETIME DEFAULT NOW(),
  UNIQUE KEY unique_judge_part_criteria (judge_user_id, participant_id, criteria_id),
  FOREIGN KEY (judge_user_id) REFERENCES users(user_id),
  FOREIGN KEY (participant_id) REFERENCES participants(participant_id),
  FOREIGN KEY (criteria_id) REFERENCES criteria(criteria_id)
);

-- 8. VOTES
CREATE TABLE votes (
  vote_id INT PRIMARY KEY AUTO_INCREMENT,
  voter_user_id INT,
  participant_id INT,
  event_id INT,
  voted_at DATETIME DEFAULT NOW(),
  UNIQUE KEY unique_voter_event (voter_user_id, event_id),
  FOREIGN KEY (voter_user_id) REFERENCES users(user_id),
  FOREIGN KEY (participant_id) REFERENCES participants(participant_id),
  FOREIGN KEY (event_id) REFERENCES events(event_id)
);

-- 9. RESULTS
CREATE TABLE results (
  result_id INT PRIMARY KEY AUTO_INCREMENT,
  event_id INT,
  participant_id INT,
  judge_score DECIMAL(6,2),
  vote_score DECIMAL(6,2),
  final_score DECIMAL(6,2),
  rank INT,
  is_winner TINYINT(1) DEFAULT 0,
  calculated_at DATETIME,
  FOREIGN KEY (event_id) REFERENCES events(event_id),
  FOREIGN KEY (participant_id) REFERENCES participants(participant_id)
);

-- =============================================
-- SAMPLE DATA
-- =============================================

-- Categories
INSERT INTO categories (name, description, icon) VALUES
('Cultural', 'Dance, music, drama and cultural performances', 'bi-music-note-beamed'),
('Technical', 'Coding, robotics and technical competitions', 'bi-cpu'),
('Sports', 'Athletic and sports competitions', 'bi-trophy'),
('Talent Show', 'Open talent showcase for all genres', 'bi-star');

-- Users: Admin
INSERT INTO users (full_name, email, phone, password, role, bio) VALUES
('Admin User', 'admin@college.edu', '9000000001', MD5('admin123'), 'admin', 'System administrator');

-- Users: Judges
INSERT INTO users (full_name, email, phone, password, role, bio) VALUES
('Dr. Ramesh Kumar', 'judge@college.edu', '9000000002', MD5('judge123'), 'judge', 'Senior faculty and cultural expert'),
('Prof. Anita Sharma', 'judge2@college.edu', '9000000003', MD5('judge123'), 'judge', 'Technical department head'),
('Mr. Suresh Patil', 'judge3@college.edu', '9000000004', MD5('judge123'), 'judge', 'Sports coordinator'),
('Ms. Priya Nair', 'judge4@college.edu', '9000000005', MD5('judge123'), 'judge', 'Arts and talent faculty');

-- Users: Participants
INSERT INTO users (full_name, email, phone, password, role, bio) VALUES
('Arjun Mehta', 'participant@college.edu', '9100000001', MD5('part123'), 'participant', 'Classical dancer and performer'),
('Sneha Reddy', 'sneha@college.edu', '9100000002', MD5('part123'), 'participant', 'Vocalist and music enthusiast'),
('Rahul Verma', 'rahul@college.edu', '9100000003', MD5('part123'), 'participant', 'Full stack developer'),
('Pooja Desai', 'pooja@college.edu', '9100000004', MD5('part123'), 'participant', 'AI/ML enthusiast'),
('Kiran Yadav', 'kiran@college.edu', '9100000005', MD5('part123'), 'participant', 'Cricket and athletics champion'),
('Divya Singh', 'divya@college.edu', '9100000006', MD5('part123'), 'participant', 'Badminton state player'),
('Mohit Joshi', 'mohit@college.edu', '9100000007', MD5('part123'), 'participant', 'Stand-up comedian and actor'),
('Kavya Iyer', 'kavya@college.edu', '9100000008', MD5('part123'), 'participant', 'Painter and multi-talent artist');

-- Users: Students
INSERT INTO users (full_name, email, phone, password, role) VALUES
('Ravi Gupta', 'student@college.edu', '9200000001', MD5('student123'), 'student'),
('Anjali Patel', 'anjali@college.edu', '9200000002', MD5('student123'), 'student'),
('Vikram Nair', 'vikram@college.edu', '9200000003', MD5('student123'), 'student'),
('Shruti Kaur', 'shruti@college.edu', '9200000004', MD5('student123'), 'student'),
('Aditya Rao', 'aditya@college.edu', '9200000005', MD5('student123'), 'student'),
('Meera Jain', 'meera@college.edu', '9200000006', MD5('student123'), 'student');

-- Events
INSERT INTO events (title, category_id, description, venue, event_date, registration_deadline, status, voting_open, scores_locked, results_announced, judge_weight, vote_weight) VALUES
('Annual Cultural Fiesta 2025', 1, 'A grand celebration of cultural performances including classical dance, music, and drama. Showcase your talent to the entire college community!', 'College Auditorium', '2025-03-15', '2025-03-10', 'Completed', 0, 1, 1, 60.00, 40.00),
('TechXtreme Hackathon', 2, 'A 24-hour coding challenge where teams solve real-world problems using innovative technology solutions.', 'Computer Lab Block B', '2025-04-20', '2025-04-15', 'Ongoing', 1, 0, 0, 60.00, 40.00),
('Sports Championship 2025', 3, 'Inter-college sports competition featuring cricket, badminton, and athletics. Represent your department with pride!', 'College Sports Ground', '2025-05-10', '2025-05-05', 'Upcoming', 0, 0, 0, 70.00, 30.00),
('Grand Talent Show', 4, 'An open platform for all genres of talent. Comedy, magic, singing, dancing — anything goes!', 'Open Air Theatre', '2025-06-01', '2025-05-25', 'Upcoming', 0, 0, 0, 50.00, 50.00);

-- Criteria for Event 1 (Cultural Fiesta)
INSERT INTO criteria (event_id, criteria_name, max_marks, description) VALUES
(1, 'Performance Quality', 10, 'Overall quality and execution of the performance'),
(1, 'Creativity & Expression', 10, 'Originality and artistic expression'),
(1, 'Stage Presence', 10, 'Confidence, energy and audience engagement');

-- Criteria for Event 2 (Hackathon)
INSERT INTO criteria (event_id, criteria_name, max_marks, description) VALUES
(2, 'Innovation', 10, 'Novelty and uniqueness of the solution'),
(2, 'Technical Implementation', 10, 'Code quality and technical execution'),
(2, 'Presentation', 10, 'Project demo and communication quality');

-- Criteria for Event 3 (Sports)
INSERT INTO criteria (event_id, criteria_name, max_marks, description) VALUES
(3, 'Athletic Performance', 10, 'Physical performance and technique'),
(3, 'Teamwork', 10, 'Cooperation and team coordination'),
(3, 'Sportsmanship', 10, 'Fair play and conduct');

-- Criteria for Event 4 (Talent Show)
INSERT INTO criteria (event_id, criteria_name, max_marks, description) VALUES
(4, 'Entertainment Value', 10, 'How entertaining and engaging the act is'),
(4, 'Originality', 10, 'Uniqueness and creative flair'),
(4, 'Audience Impact', 10, 'Crowd reaction and emotional impact');

-- Participants (user_id 6-13 are participants)
-- Event 1: Arjun Mehta, Sneha Reddy
INSERT INTO participants (user_id, event_id, performance_title, category_entry, status) VALUES
(6, 1, 'Bharatanatyam Recital', 'Classical Dance', 'Approved'),
(7, 1, 'Carnatic Vocal Medley', 'Classical Music', 'Approved');

-- Event 2: Rahul Verma, Pooja Desai
INSERT INTO participants (user_id, event_id, performance_title, category_entry, status) VALUES
(8, 2, 'Smart Campus IoT System', 'Web Development', 'Approved'),
(9, 2, 'AI Crop Disease Detector', 'Machine Learning', 'Approved');

-- Event 3: Kiran Yadav, Divya Singh
INSERT INTO participants (user_id, event_id, performance_title, category_entry, status) VALUES
(10, 3, 'Cricket All-rounder', 'Cricket', 'Approved'),
(11, 3, 'Badminton Doubles', 'Badminton', 'Approved');

-- Event 4: Mohit Joshi, Kavya Iyer
INSERT INTO participants (user_id, event_id, performance_title, category_entry, status) VALUES
(12, 4, 'Stand-up Comedy Act', 'Comedy', 'Pending'),
(13, 4, 'Live Painting & Poetry', 'Art', 'Pending');

-- Judge Assignments
-- Event 1: Judge 1, Judge 4
INSERT INTO judge_assignments (judge_user_id, event_id) VALUES (2, 1), (5, 1);
-- Event 2: Judge 2
INSERT INTO judge_assignments (judge_user_id, event_id) VALUES (3, 2);
-- Event 3: Judge 3
INSERT INTO judge_assignments (judge_user_id, event_id) VALUES (4, 3);
-- Event 4: Judge 4
INSERT INTO judge_assignments (judge_user_id, event_id) VALUES (5, 4);

-- Scores for Event 1 by Judge 1 (user_id=2)
-- Participant 1 (Arjun): criteria 1,2,3
INSERT INTO scores (judge_user_id, participant_id, criteria_id, marks) VALUES
(2, 1, 1, 9.0), (2, 1, 2, 8.5), (2, 1, 3, 9.5),
(2, 2, 1, 7.5), (2, 2, 2, 8.0), (2, 2, 3, 7.0);

-- Scores for Event 1 by Judge 4 (user_id=5)
INSERT INTO scores (judge_user_id, participant_id, criteria_id, marks) VALUES
(5, 1, 1, 8.5), (5, 1, 2, 9.0), (5, 1, 3, 8.0),
(5, 2, 1, 8.0), (5, 2, 2, 7.5), (5, 2, 3, 8.5);

-- Scores for Event 2 by Judge 2 (user_id=3)
INSERT INTO scores (judge_user_id, participant_id, criteria_id, marks) VALUES
(3, 3, 4, 9.0), (3, 3, 5, 8.5), (3, 3, 6, 9.0),
(3, 4, 4, 8.0), (3, 4, 5, 9.0), (3, 4, 6, 8.5);

-- Votes for Event 1 (students vote)
-- user_id 14-19 are students
INSERT INTO votes (voter_user_id, participant_id, event_id) VALUES
(14, 1, 1),
(15, 1, 1),
(16, 2, 1),
(17, 1, 1),
(18, 2, 1),
(19, 1, 1);

-- Votes for Event 2
INSERT INTO votes (voter_user_id, participant_id, event_id) VALUES
(14, 3, 2),
(15, 4, 2),
(16, 3, 2),
(17, 3, 2),
(18, 4, 2),
(19, 3, 2);

-- Pre-calculated results for Event 1 (results_announced=1)
-- Arjun: judge avg = (9+8.5+9.5+8.5+9+8)/6 = 52.5/6 = 8.75 out of 10 → 87.5 normalized
-- Sneha: judge avg = (7.5+8+7+8+7.5+8.5)/6 = 46.5/6 = 7.75 → 77.5 normalized
-- Arjun votes = 4, Sneha votes = 2, total = 6
-- Arjun vote_score = 4/6 * 100 = 66.67, Sneha = 2/6 * 100 = 33.33
-- Arjun final = 87.5*0.6 + 66.67*0.4 = 52.5 + 26.67 = 79.17
-- Sneha final = 77.5*0.6 + 33.33*0.4 = 46.5 + 13.33 = 59.83
INSERT INTO results (event_id, participant_id, judge_score, vote_score, final_score, rank, is_winner, calculated_at) VALUES
(1, 1, 87.50, 66.67, 79.17, 1, 1, NOW()),
(1, 2, 77.50, 33.33, 59.83, 2, 0, NOW());
