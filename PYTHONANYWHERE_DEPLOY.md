# 🚀 Инструкция по развертыванию на PythonAnywhere

## Шаг 1: Регистрация на PythonAnywhere
1. Перейдите на https://www.pythonanywhere.com/
2. Создайте бесплатный аккаунт (Beginner account)
3. Подтвердите email

## Шаг 2: Загрузка файлов проекта
1. Войдите в свой аккаунт PythonAnywhere
2. Перейдите в "Files" (Файлы)
3. Создайте папку `flight_service`
4. Загрузите все файлы из папки `backend` в `flight_service/`

### Альтернативный способ через Git:
1. Откройте "Bash Console" 
2. Выполните команды:
```bash
git clone https://github.com/yourusername/flight-service-kg.git
cd flight-service-kg/backend
```

## Шаг 3: Установка зависимостей
1. Откройте "Bash Console"
2. Перейдите в папку проекта:
```bash
cd ~/flight_service
```
3. Установите зависимости:
```bash
pip3.10 install --user -r requirements.txt
```

## Шаг 4: Настройка веб-приложения
1. Перейдите в "Web" в панели управления
2. Нажмите "Add a new web app"
3. Выберите "Manual configuration"
4. Выберите Python 3.10
5. В разделе "Code" укажите:
   - Source code: `/home/yourusername/flight_service`
   - Working directory: `/home/yourusername/flight_service`

## Шаг 5: Настройка WSGI файла
1. В разделе "Code" нажмите на ссылку WSGI configuration file
2. Замените содержимое файла на:

```python
import sys
import os

# Добавляем путь к нашему приложению
path = '/home/yourusername/flight_service'
if path not in sys.path:
    sys.path.insert(0, path)

# Устанавливаем переменные окружения для продакшена
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'your-super-secret-production-key-here'
os.environ['DATABASE_URL'] = 'sqlite:///instance/flight_service.db'
os.environ['APP_URL'] = 'https://yourusername.pythonanywhere.com'

from app import create_app

# Создаем приложение
application = create_app()
```

**Важно:** Замените `yourusername` на ваше имя пользователя PythonAnywhere!

## Шаг 6: Инициализация базы данных
1. В Bash Console выполните:
```bash
cd ~/flight_service
python3.10 init_production_db.py
```

## Шаг 7: Настройка статических файлов
1. В разделе "Static files" добавьте:
   - URL: `/static/`
   - Directory: `/home/yourusername/flight_service/app/static/`

## Шаг 8: Запуск приложения
1. Нажмите "Reload" в разделе Web
2. Ваше приложение будет доступно по адресу: `https://yourusername.pythonanywhere.com`

## 🔐 Первый вход
- Логин: `admin`
- Пароль: `admin123`

**Обязательно смените пароль после первого входа!**

## 📱 Совместимость с устройствами

Ваш сайт будет работать на всех устройствах:

### ✅ Поддерживаемые устройства:
- **Компьютеры** (Windows, Mac, Linux)
- **Смартфоны** (Android, iPhone)
- **Планшеты** (iPad, Android tablets)
- **Smart TV** (с браузером)

### ✅ Поддерживаемые браузеры:
- Chrome
- Firefox
- Safari
- Edge
- Opera
- Мобильные браузеры

### 📱 Адаптивный дизайн:
Сайт автоматически адаптируется под размер экрана благодаря Bootstrap CSS framework.

## 🛠 Устранение неполадок

### Ошибка 500:
1. Проверьте логи в разделе "Error log"
2. Убедитесь, что все пути в WSGI файле правильные
3. Проверьте, что база данных инициализирована

### Статические файлы не загружаются:
1. Проверьте настройки Static files
2. Убедитесь, что пути правильные

### База данных не работает:
1. Запустите заново `init_production_db.py`
2. Проверьте права доступа к папке `instance`

## 🔄 Обновление проекта
Для обновления кода:
1. Загрузите новые файлы
2. Нажмите "Reload" в разделе Web
3. При необходимости обновите базу данных

## 📞 Поддержка
Если возникнут проблемы:
1. Проверьте логи ошибок в PythonAnywhere
2. Обратитесь к документации PythonAnywhere
3. Задайте вопрос в форуме PythonAnywhere