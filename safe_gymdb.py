import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'gym.db')

sql = '''
-- Тренеры
INSERT INTO trainers (name, specialization, photo, experience) VALUES
('Арай Кайратовна', 'Йога', '/static/images/anna.jpg', 5),
('Арсен Тимурович', 'Тяжелая атлетика', '/static/images/ivan.jpg', 8);

-- Тренировки
INSERT INTO workouts (title, trainer_id, date, time, max_slots, booked_slots) VALUES
('Утренняя Йога', 1, '2025-12-01', '09:00', 12, 2),
('Обеденная физическая тренировка', 2, '2025-12-01', '18:30', 10, 1),
('КроссФит', 2, '2025-12-02', '07:00', 15, 0);

-- Тестовый пользователь
INSERT INTO users (name, email, password, phone) VALUES
('Test User', 'test@example.com', 'password123', '+70000000000');

-- Настройки
INSERT INTO settings (gym_name, allow_registration) VALUES ('VozFitness', 1);
'''

with sqlite3.connect(DB_PATH) as conn:
    cur = conn.cursor()
    for statement in sql.split(';'):
        stmt = statement.strip()
        if stmt:
            cur.execute(stmt)
    conn.commit()
print('Тестовые данные успешно восстановлены!')
