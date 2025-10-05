import sqlite3

# Подключаемся к базе данных
conn = sqlite3.connect('flight_service.db')
cursor = conn.cursor()

# Получаем список таблиц
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print('Таблицы в базе данных:')
for table in tables:
    print(f'- {table[0]}')

# Пробуем добавить колонки если таблица user существует
try:
    cursor.execute("SELECT 1 FROM user LIMIT 1")
    print('\nТаблица user найдена. Добавляем колонки...')
    
    try:
        cursor.execute('ALTER TABLE user ADD COLUMN is_email_confirmed BOOLEAN DEFAULT 0')
        print('✓ Колонка is_email_confirmed добавлена')
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print('✓ Колонка is_email_confirmed уже существует')
        else:
            print(f'✗ Ошибка при добавлении is_email_confirmed: {e}')
    
    try:
        cursor.execute('ALTER TABLE user ADD COLUMN email_confirmed_at DATETIME')
        print('✓ Колонка email_confirmed_at добавлена')
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print('✓ Колонка email_confirmed_at уже существует')
        else:
            print(f'✗ Ошибка при добавлении email_confirmed_at: {e}')
    
    conn.commit()
    print('\nИзменения сохранены в базу данных')
    
except sqlite3.OperationalError:
    print('\nТаблица user не найдена')

conn.close()