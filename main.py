try:
    from flask import Flask, request, jsonify, send_from_directory
except Exception:
    import sys
    import subprocess
    try:
        print('Flask not found — installing Flask...')
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'Flask==2.3.2'])
        # проблема с импортом
        from flask import Flask, request, jsonify, send_from_directory
    except Exception as e:
        raise ImportError(
            "Flask не найден и автоматическая установка не удалась. \n"
            "Установите Flask вручную: python -m pip install Flask"
        ) from e
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash

# Путь к базе и шаблонам
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "gym.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")

# Flask-приложение, пусть будет
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, 'static'), template_folder=os.path.join(BASE_DIR, 'templates'))

### функция для базы, если вдруг что-то пойдет не так
def get_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON')
        return conn
    except Exception as err:
        print('База не открылась, ну и ладно:', err)
        return None

# Инициализация базы
def init_db():
    # Если базы нет — создаём, если есть — забиваем
    if not os.path.exists(DB_PATH):
        print('Базы нет, создаём...')
        # Можно было бы тут что-то сделать, но лень
    else:
        print('База уже есть, не трогаем')


init_db()

@app.route('/api/register', methods=['POST'])
def register():
    """
    Регистрация нового пользователя. Можно просто email и пароль, остальное по желанию.
    """
    data = request.get_json() or {}
    # email и пароль
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'email и пароль нужны!'}), 400

    # Если имя не указано — берём из email
    name = data.get('name') or (data.get('email').split('@')[0] if data.get('email') else 'Безымянный')
    try:
        hashed = generate_password_hash(data.get('password'))
        conn = get_db()
        if conn:
            cur = conn.execute(
                'INSERT INTO users (name, email, password, phone) VALUES (?, ?, ?, ?)',
                (name, data.get('email'), hashed, data.get('phone'))
            )
            user_id = cur.lastrowid
            conn.commit()
            return jsonify({'id': user_id, 'name': name, 'email': data.get('email')}), 201
        else:
            return jsonify({'error': 'База не отвечает'}), 500
    except sqlite3.IntegrityError as e:
        return jsonify({'error': 'Такой email уже занят'}), 400


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'email и пароль нужны!'}), 400
    conn = get_db()
    if conn:
        cur = conn.execute('SELECT id, name, email, phone, password FROM users WHERE email = ?', (data['email'],))
        user = cur.fetchone()
        if not user:
            return jsonify({'error': 'Нет такого пользователя'}), 401
        stored = user['password']
        if not check_password_hash(stored, data['password']):
            return jsonify({'error': 'Пароль неверный'}), 401
        # Не возвращаем пароль
        user_dict = dict(user)
        user_dict.pop('password', None)
        return jsonify(user_dict), 200


@app.route('/api/profile', methods=['GET'])
def profile():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id нужен как query param'}), 400
    conn = get_db()
    if conn:
        cur = conn.execute('SELECT id, name, email, phone FROM users WHERE id = ?', (user_id,))
        user = cur.fetchone()
        if not user:
            return jsonify({'error': 'Пользователь не найден'}), 404
        return jsonify(dict(user))


@app.route('/api/trainers', methods=['GET'])
def get_trainers():
    # Просто возвращаем всех тренеров,если они есть
    conn = get_db()
    if conn:
        cur = conn.execute('SELECT id, name, specialization, photo, experience FROM trainers')
        trainers = [dict(row) for row in cur.fetchall()]
        return jsonify(trainers)


@app.route('/api/workouts', methods=['GET'])
def get_workouts():
    # Возвращаем все тренировки 
    conn = get_db()
    if conn:
        cur = conn.execute('''
            SELECT w.id, w.title, w.trainer_id, w.date, w.time, w.max_slots, w.booked_slots,
                        t.name as trainer_name, t.specialization
            FROM workouts w
            LEFT JOIN trainers t ON w.trainer_id = t.id
            ORDER BY w.date, w.time
        ''')
        rows = [dict(r) for r in cur.fetchall()]
        # Считаем свободные места
        for r in rows:
            r['available_slots'] = r['max_slots'] - r['booked_slots']
        return jsonify(rows)


@app.route('/api/book', methods=['POST'])
def book_workout():
    """
    Забронировать тренировку: JSON {user_id, workout_id}
    """
    data = request.get_json() or {}
    if not data.get('user_id') or not data.get('workout_id'):
        return jsonify({'error': 'user_id и workout_id нужны!'}), 400
    user_id = data['user_id']
    workout_id = data['workout_id']
    conn = get_db()
    if conn:
        cur = conn.execute('SELECT max_slots, booked_slots FROM workouts WHERE id = ?', (workout_id,))
        w = cur.fetchone()
        if not w:
            return jsonify({'error': 'Тренировка не найдена'}), 404
        if w['booked_slots'] >= w['max_slots']:
            return jsonify({'error': 'Нет свободных мест'}), 400
        # просто бронируем
        try:
            conn.execute('INSERT INTO bookings (user_id, workout_id, status) VALUES (?, ?, ?)', (user_id, workout_id, 'booked'))
            conn.execute('UPDATE workouts SET booked_slots = booked_slots + 1 WHERE id = ?', (workout_id,))
            conn.commit()
            return jsonify({'message': 'Забронировано'}), 201
        except sqlite3.IntegrityError as e:
            return jsonify({'error': 'Ошибка бронирования'}), 400


@app.route('/api/cancel', methods=['POST'])
def cancel_booking():
    """
    Отмена брони: JSON {user_id, workout_id} — меняет статус и освобождает место
    """
    data = request.get_json() or {}
    if not data.get('user_id') or not data.get('workout_id'):
        return jsonify({'error': 'user_id и workout_id нужны!'}), 400
    user_id = data['user_id']
    workout_id = data['workout_id']
    conn = get_db()
    if conn:
        cur = conn.execute('SELECT id, status FROM bookings WHERE user_id = ? AND workout_id = ? AND status = ?', (user_id, workout_id, 'booked'))
        b = cur.fetchone()
        if not b:
            return jsonify({'error': 'Бронь не найдена'}), 404
        conn.execute('UPDATE bookings SET status = ? WHERE id = ?', ('cancelled', b['id']))
        conn.execute('UPDATE workouts SET booked_slots = booked_slots - 1 WHERE id = ?', (workout_id,))
        conn.commit()
        return jsonify({'message': 'Отменено'})


@app.route('/api/my_bookings', methods=['GET'])
def my_bookings():
    """
    Вернуть список активных броней пользователя. Query param: user_id
    """
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id нужен как query param'}), 400
    conn = get_db()
    if conn:
        cur = conn.execute('''
            SELECT b.id as booking_id, b.workout_id, b.status,
            w.title, w.date, w.time, w.max_slots, w.booked_slots,
                t.name as trainer_name
            FROM bookings b
            JOIN workouts w ON b.workout_id = w.id
            LEFT JOIN trainers t ON w.trainer_id = t.id
            WHERE b.user_id = ? AND b.status = ?
            ORDER BY w.date, w.time
        ''', (user_id, 'booked'))
        rows = [dict(r) for r in cur.fetchall()]
        for r in rows:
            r['available_slots'] = r['max_slots'] - r['booked_slots']
        return jsonify(rows)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    # отдаём файлы из templates
    if path == '' or path == 'index.html':
        return send_from_directory(os.path.join(BASE_DIR, 'templates'), 'index.html')
    # Защита не даём ходить по папкам
    safe_path = os.path.normpath(path)
    if safe_path.startswith('templates') or '..' in safe_path:
        return '', 404
    if os.path.exists(os.path.join(BASE_DIR, 'templates', safe_path)):
        return send_from_directory(os.path.join(BASE_DIR, 'templates'), safe_path)
    return send_from_directory(os.path.join(BASE_DIR, 'templates'), 'index.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
