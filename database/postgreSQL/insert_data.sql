--Insert Roles
INSERT INTO roles (id, role_name)
VALUES
(1,'Creator'),
(2,'Agency'),
(3,'Marketing Team'),
(4,'Administrator');

--Insert into Users table
INSERT INTO users
(id, full_name, email, phone_number, password_hash, role_id)
VALUES
('crt11','Rahul Sharma','rahul@gmail.com','9876543210','hashed_password1',1),

('crt32','Priya Reddy','priya@gmail.com','9876543211','hashed_password2',1),

('agc21','ABC Agency','agency@gmail.com','9876543212','hashed_password3',2);

--Insert creator profiles
INSERT INTO creator_profiles
(id, user_id, username, bio, youtube_url, instagram_url, linkedin_url)
VALUES
('crt11','crt11','rahulYT','Tech Content Creator',
'https://youtube.com/@rahul',
'https://instagram.com/rahul',
'https://linkedin.com/in/rahul'),

('crt32','crt32','priyaCodes','Programming Tutorials',
'https://youtube.com/@priya',
'https://instagram.com/priya',
'https://linkedin.com/in/priya');

--Insert into Agency Profiles
INSERT INTO agency_profiles
(id, user_id, agency_name, website, contact_number)
VALUES
('agc21','agc21',
'ABC Digital Agency',
'https://abcagency.com',
'9876543210');

--Insert into account settings
INSERT INTO account_settings
(id, user_id, theme, notifications, language)
VALUES
('set11','crt11','Dark',TRUE,'English'),
('set32','crt32','Light',TRUE,'English'),
('set21','agc21','Dark',FALSE,'English');

--Insert into agency creators
INSERT INTO agency_creators
(id, agency_id, creator_id)
VALUES
('map11','agc21','crt11'),
('map12','agc21','crt32');

