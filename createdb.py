import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'gym.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')

with open(SCHEMA_PATH, encoding='utf-8') as f:
    schema_sql = f.read()

with sqlite3.connect(DB_PATH) as conn:
    cur = conn.cursor()
    for statement in schema_sql.split(';'):
        stmt = statement.strip()
        if stmt:
            try:
                cur.execute(stmt)
            except Exception as e:
                print(f'Ошибка при выполнении: {stmt[:50]}...\n{e}')
    conn.commit()
print('Структура базы данных успешно создана!')
