USE event_management_db;

INSERT INTO categories (name, description) VALUES 
('Music', 'Music competitions'),
('Dance', 'Dance events'),
('Drama', 'Theater and acting');

INSERT INTO events (title, category_id, description, event_date, status) VALUES 
('Annual Music Fest', 1, 'Showcase your musical talents', '2026-03-15', 'Upcoming'),
('Dance Battle', 2, 'Dance competition', '2026-03-20', 'Upcoming'),
('Drama Play', 3, 'Stage performance', '2026-03-25', 'Upcoming');