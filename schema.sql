PRAGMA foreign_keys = ON;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- айдишник
    name TEXT NOT NULL, -- имя
    email TEXT NOT NULL UNIQUE, -- почта
    password TEXT NOT NULL, -- пароль
    phone TEXT -- телефон
);

CREATE TABLE trainers (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- тренерский айди
    name TEXT NOT NULL, -- имя тренера
    specialization TEXT, -- чем занимается
    photo TEXT, -- фотка
    experience INTEGER -- опыт
);

CREATE TABLE workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- айди тренировки
    title TEXT NOT NULL, -- название
    trainer_id INTEGER, -- кто ведёт
    date TEXT NOT NULL, -- когда
    time TEXT NOT NULL, -- во сколько
    max_slots INTEGER NOT NULL DEFAULT 10, -- сколько мест
    booked_slots INTEGER NOT NULL DEFAULT 0, -- сколько уже занято
    FOREIGN KEY (trainer_id) REFERENCES trainers(id) ON DELETE SET NULL -- если тренер ушёл
);

CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- айди брони
    user_id INTEGER NOT NULL, -- кто бронирует
    workout_id INTEGER NOT NULL, -- что бронирует
    status TEXT NOT NULL DEFAULT 'booked', -- статус
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE, -- если пользователь удалён
    FOREIGN KEY (workout_id) REFERENCES workouts(id) ON DELETE CASCADE -- если тренировка удалена
);

CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- айди настройки
    gym_name TEXT, -- название зала
    allow_registration INTEGER DEFAULT 1 -- можно ли регистрироваться
);

-- Добавим пару тренеров для теста
INSERT INTO trainers (name, specialization, photo, experience) VALUES
('Арай Кайратовна', 'Йога', '/static/images/anna.jpg', 5),
('Арсен Тимурович', 'Тяжелая атлетика', '/static/images/ivan.jpg', 8);

-- Тренировки для разнообразия
INSERT INTO workouts (title, trainer_id, date, time, max_slots, booked_slots) VALUES
('Утренняя Йога', 1, '2025-12-01', '09:00', 12, 2),
('Обеденная физическая тренировка', 2, '2025-12-01', '18:30', 10, 1),
('КроссФит', 2, '2025-12-02', '07:00', 15, 0);

-- Тестовый пользователь, не обращайте внимания
INSERT INTO users (name, email, password, phone) VALUES
('Test User', 'test@example.com', 'password123', '+70000000000');

-- Настройки зала
INSERT INTO settings (gym_name, allow_registration) VALUES ('VozFitness', 1);

