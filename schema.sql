DROP TABLE IF EXISTS students;

CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    marks INTEGER NOT NULL,
    grade TEXT
);

INSERT INTO students (name, marks, grade) VALUES
('Alice', 85, 'A'),
('Bob', 92, 'A+'),
('Charlie', 70, 'B'),
('Daisy', 59, 'C'),
('Ethan', 95, 'A+');
