#!/usr/bin/env python3
"""
Скрипт для добавления полей профиля в базу данных
"""

import sqlite3
import os

def add_profile_fields():
    """Добавляет поля профиля в таблицу user"""
    
    db_path = 'instance/flight_service.db'
    
    if not os.path.exists(db_path):
        print("База данных не найдена. Создайте её заново с помощью seed_db.py")
        return
    
    # Создаем бэкап
    backup_path = 'flight_service_backup.db'
    import shutil
    shutil.copy2(db_path, backup_path)
    print(f"Создан бэкап: {backup_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Проверяем, существуют ли новые поля
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        new_fields = ['phone', 'birth_date', 'passport_number', 'address', 
                     'nationality', 'avatar_filename', 'bio', 'updated_at']
        
        missing_fields = [field for field in new_fields if field not in columns]
        
        if not missing_fields:
            print("Все поля профиля уже существуют в базе данных.")
            return
        
        print(f"Добавляем поля: {', '.join(missing_fields)}")
        
        # Добавляем отсутствующие поля
        for field in missing_fields:
            if field == 'phone':
                cursor.execute('ALTER TABLE user ADD COLUMN phone VARCHAR(20)')
            elif field == 'birth_date':
                cursor.execute('ALTER TABLE user ADD COLUMN birth_date DATE')
            elif field == 'passport_number':
                cursor.execute('ALTER TABLE user ADD COLUMN passport_number VARCHAR(50)')
            elif field == 'address':
                cursor.execute('ALTER TABLE user ADD COLUMN address TEXT')
            elif field == 'nationality':
                cursor.execute('ALTER TABLE user ADD COLUMN nationality VARCHAR(50)')
            elif field == 'avatar_filename':
                cursor.execute('ALTER TABLE user ADD COLUMN avatar_filename VARCHAR(255)')
            elif field == 'bio':
                cursor.execute('ALTER TABLE user ADD COLUMN bio TEXT')
            elif field == 'updated_at':
                cursor.execute("ALTER TABLE user ADD COLUMN updated_at DATETIME")
        
        conn.commit()
        print("✅ Поля профиля успешно добавлены!")
        print("✅ Теперь пользователи могут редактировать свои профили")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Ошибка: {e}")
        # Восстанавливаем из бэкапа
        conn.close()
        shutil.copy2(backup_path, db_path)
        print("🔄 База данных восстановлена из бэкапа")
        
    finally:
        conn.close()

if __name__ == '__main__':
    add_profile_fields()