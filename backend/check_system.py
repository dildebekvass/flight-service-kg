#!/usr/bin/env python3
"""
Скрипт для проверки работоспособности системы на PythonAnywhere
"""

import os
import sys

def check_system():
    """Проверка системы"""
    print("🔍 Проверка системы Flight Service KG")
    print("=" * 50)
    
    # Проверка Python версии
    print(f"✅ Python версия: {sys.version}")
    
    # Проверка пути
    current_path = os.getcwd()
    print(f"✅ Текущая папка: {current_path}")
    
    # Проверка файлов
    required_files = [
        'app/__init__.py',
        'app/models.py',
        'app/routes.py',
        'config.py',
        'requirements.txt'
    ]
    
    print("\n📁 Проверка файлов:")
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - ОТСУТСТВУЕТ!")
    
    # Проверка зависимостей
    print("\n📦 Проверка зависимостей:")
    try:
        import flask
        print(f"✅ Flask: {flask.__version__}")
    except ImportError:
        print("❌ Flask не установлен!")
    
    try:
        import flask_sqlalchemy
        print(f"✅ Flask-SQLAlchemy: {flask_sqlalchemy.__version__}")
    except ImportError:
        print("❌ Flask-SQLAlchemy не установлен!")
    
    try:
        import flask_login
        print(f"✅ Flask-Login: {flask_login.__version__}")
    except ImportError:
        print("❌ Flask-Login не установлен!")
    
    # Проверка базы данных
    print("\n🗃️ Проверка базы данных:")
    if os.path.exists('instance/flight_service.db'):
        print("✅ База данных найдена")
        
        # Попытка подключения
        try:
            from app import create_app, db
            from app.models import User, Company, Flight
            
            app = create_app()
            with app.app_context():
                users_count = User.query.count()
                companies_count = Company.query.count()
                flights_count = Flight.query.count()
                
                print(f"✅ Пользователей: {users_count}")
                print(f"✅ Компаний: {companies_count}")
                print(f"✅ Рейсов: {flights_count}")
                
        except Exception as e:
            print(f"❌ Ошибка подключения к БД: {e}")
    else:
        print("❌ База данных не найдена! Запустите init_production_db.py")
    
    # Проверка переменных окружения
    print("\n🔧 Переменные окружения:")
    env_vars = ['FLASK_ENV', 'SECRET_KEY', 'DATABASE_URL']
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            if var == 'SECRET_KEY':
                print(f"✅ {var}: {'*' * len(value)}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"⚠️ {var}: не установлена")
    
    print("\n" + "=" * 50)
    print("🚀 Проверка завершена!")

if __name__ == '__main__':
    check_system()