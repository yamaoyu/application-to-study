create DATABASE IF NOT EXISTS study_app;
create DATABASE IF NOT EXISTS test_study_app;

GRANT ALL PRIVILEGES ON study_app.* TO 'study1'@'%';
GRANT ALL PRIVILEGES ON test_study_app.* TO 'study1'@'%';
FLUSH PRIVILEGES;