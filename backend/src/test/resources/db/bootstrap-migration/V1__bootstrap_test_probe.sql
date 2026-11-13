CREATE TABLE bootstrap_test_probe (id INTEGER PRIMARY KEY, marker TEXT NOT NULL);
GRANT SELECT, INSERT ON TABLE bootstrap_test_probe TO lumia_app;
