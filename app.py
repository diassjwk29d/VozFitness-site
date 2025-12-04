
# Просто запускалка
from main import app

if __name__ == '__main__':
    # Запускаем сервер
    app.run(debug=True, host='0.0.0.0', port=5000)
