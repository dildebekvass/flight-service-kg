#!/var/www/your_username_pythonanywhere.com_wsgi.py

import sys
import os

# Добавляем путь к нашему приложению
path = '/home/yourusername/flight_service/backend'
if path not in sys.path:
    sys.path.insert(0, path)

# Устанавливаем переменные окружения для продакшена
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'your-super-secret-production-key-here'
os.environ['DATABASE_URL'] = 'sqlite:///instance/flight_service.db'

from app import create_app

# Создаем приложение
application = create_app()

if __name__ == "__main__":
    application.run()