#!/usr/bin/env python3
"""
Скрипт для удаления полей подтверждения email из базы данных
"""

import sqlite3
import os

def remove_email_confirmation_fields():
    """Удаляет поля подтверждения email из таблицы user"""
    
    db_path = 'flight_service.db'
    
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
        # Проверяем, существуют ли поля
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_email_confirmed' not in columns and 'email_confirmed_at' not in columns:
            print("Поля подтверждения email уже удалены из базы данных.")
            return
        
        print("Удаляем поля подтверждения email...")
        
        # Создаем новую таблицу без полей подтверждения
        cursor.execute('''
            CREATE TABLE user_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(120) NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(200) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'user',
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Копируем данные из старой таблицы
        cursor.execute('''
            INSERT INTO user_new (id, name, email, password_hash, role, is_active, created_at)
            SELECT id, name, email, password_hash, role, is_active, created_at
            FROM user
        ''')
        
        # Удаляем старую таблицу и переименовываем новую
        cursor.execute('DROP TABLE user')
        cursor.execute('ALTER TABLE user_new RENAME TO user')
        
        conn.commit()
        print("✅ Поля подтверждения email успешно удалены!")
        print("✅ Все пользователи теперь могут входить без подтверждения email")
        
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
    remove_email_confirmation_fields()