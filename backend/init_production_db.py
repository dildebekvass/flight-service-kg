#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных на PythonAnywhere
Запустите этот файл один раз после загрузки проекта
"""

import os
import sys

# Добавляем путь к приложению
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.insert(0, path)

from app import create_app, db
from app.models import User, Company, Flight, Ticket

def init_db():
    """Инициализация базы данных"""
    print("Инициализация базы данных...")
    
    # Создаем экземпляр приложения
    app = create_app()
    
    with app.app_context():
        # Создаем все таблицы
        db.create_all()
        print("Таблицы созданы!")
        
        # Проверяем есть ли уже пользователи
        if not User.query.first():
            print("Создание администратора...")
            admin = User(
                username='admin',
                email='admin@flightservice.kg',
                first_name='Admin',
                last_name='User',
                is_admin=True,
                is_confirmed=True
            )
            admin.set_password('admin123')  # Смените пароль!
            db.session.add(admin)
            db.session.commit()
            print("Администратор создан! Логин: admin, Пароль: admin123")
        
        print("База данных готова к работе!")

if __name__ == '__main__':
    init_db()