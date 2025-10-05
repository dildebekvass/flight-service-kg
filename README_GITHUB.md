# ✈️ Flight Service KG

> Система управления авиабилетами для Кыргызстана

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Issues](https://img.shields.io/github/issues/dildebekvass/flight-service-kg)](https://github.com/dildebekvass/flight-service-kg/issues)
[![GitHub Stars](https://img.shields.io/github/stars/dildebekvass/flight-service-kg)](https://github.com/dildebekvass/flight-service-kg/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/dildebekvass/flight-service-kg)](https://github.com/dildebekvass/flight-service-kg/network)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/dildebekvass/flight-service-kg/graphs/commit-activity)

## 🌟 Описание проекта

Flight Service KG - это веб-приложение для управления авиаперевозками, разработанное специально для рынка Кыргызстана. Система позволяет авиакомпаниям управлять рейсами, а пассажирам - бронировать билеты онлайн.

## 🚀 Основные возможности

### 👥 Для пассажиров:
- ✅ Поиск и бронирование авиабилетов
- ✅ Просмотр истории бронирований
- ✅ Управление профилем
- ✅ QR-код для оплаты билетов
- ✅ Адаптивный дизайн для всех устройств

### 🏢 Для авиакомпаний:
- ✅ Управление рейсами
- ✅ Просмотр пассажиров
- ✅ Статистика продаж
- ✅ Управление профилем компании

### 👨‍💼 Для администраторов:
- ✅ Управление пользователями
- ✅ Управление авиакомпаниями
- ✅ Модерация контента
- ✅ Системная статистика

## 🛠 Технологии

- **Backend**: Python 3.11, Flask 2.3.3
- **Database**: SQLite (для разработки), PostgreSQL (для продакшена)
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF
- **Migration**: Flask-Migrate

## 📱 Совместимость

Приложение работает на всех современных устройствах:
- 💻 **Компьютеры** (Windows, Mac, Linux)
- 📱 **Смартфоны** (Android, iOS)
- 📲 **Планшеты** (iPad, Android tablets)
- 📺 **Smart TV** (с браузером)

## 🚀 Быстрый старт

### Локальная разработка

1. **Клонируйте репозиторий**
```bash
git clone https://github.com/dildebekvaas/flight-service-kg.git
cd flight-service-kg
```

2. **Создайте виртуальную среду**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. **Установите зависимости**
```bash
cd backend
pip install -r requirements.txt
```

4. **Инициализируйте базу данных**
```bash
python seed_db.py
```

5. **Запустите приложение**
```bash
python run.py
```

Приложение будет доступно по адресу: http://127.0.0.1:5000

### 🔐 Тестовые данные

**Администратор:**
- Логин: `admin`
- Пароль: `admin123`

**Авиакомпания:**
- Логин: `airkg`
- Пароль: `password123`

**Пользователь:**
- Логин: `testuser`
- Пароль: `password123`

## 🌐 Развертывание

### PythonAnywhere (Рекомендуется)

Подробная инструкция по развертыванию находится в файле [PYTHONANYWHERE_DEPLOY.md](PYTHONANYWHERE_DEPLOY.md).

### Heroku

```bash
# Установите Heroku CLI
# Создайте приложение
heroku create your-app-name

# Добавьте переменные окружения
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key

# Деплой
git push heroku main
```

## 📁 Структура проекта

```
flight-service-kg/
├── backend/                    # Основное приложение
│   ├── app/                   # Flask приложение
│   │   ├── static/           # Статические файлы (CSS, JS, изображения)
│   │   ├── templates/        # HTML шаблоны
│   │   ├── __init__.py      # Инициализация Flask
│   │   ├── models.py        # Модели базы данных
│   │   ├── routes.py        # Маршруты приложения
│   │   ├── forms.py         # Формы WTF
│   │   └── utils.py         # Вспомогательные функции
│   ├── instance/             # База данных
│   ├── config.py            # Конфигурация
│   ├── requirements.txt     # Python зависимости
│   ├── run.py              # Точка входа
│   └── seed_db.py          # Инициализация БД
├── docs/                    # Документация
├── README.md               # Этот файл
└── .gitignore             # Git исключения
```

## 🔧 API Endpoints

### Аутентификация
- `POST /login` - Вход в систему
- `POST /signup` - Регистрация
- `GET /logout` - Выход

### Рейсы
- `GET /` - Главная страница с поиском
- `GET /search` - Поиск рейсов
- `GET /flight/<id>` - Детали рейса

### Бронирование
- `POST /book/<flight_id>` - Бронирование билета
- `GET /tickets` - История бронирований

### Управление (для авиакомпаний)
- `GET /company/dashboard` - Панель управления
- `POST /company/flight/add` - Добавление рейса
- `PUT /company/flight/<id>` - Редактирование рейса

## 🧪 Тестирование

```bash
# Запуск тестов
python -m pytest tests/

# Покрытие кода
python -m pytest --cov=app tests/
```

## 📊 База данных

### Модели:
- **User** - Пользователи системы
- **Company** - Авиакомпании
- **Flight** - Рейсы
- **Ticket** - Билеты

### Схема базы данных:
```sql
Users (id, username, email, password_hash, first_name, last_name, ...)
Companies (id, name, email, description, contact_info, ...)
Flights (id, company_id, flight_number, departure_city, ...)
Tickets (id, user_id, flight_id, seat_number, price, ...)
```

## 🤝 Участие в разработке

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/AmazingFeature`)
3. Зафиксируйте изменения (`git commit -m 'Add some AmazingFeature'`)
4. Отправьте в ветку (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📝 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

## 👤 Автор

**Разработчик:** Dildebek
- GitHub: [@dildebekvaas](https://github.com/dildebekvaas)
- Email: your-email@example.com

## 🙏 Благодарности

- Flask команде за отличный веб-фреймворк
- Bootstrap за адаптивный CSS фреймворк
- Сообществу Python за отличные библиотеки

## 📞 Поддержка

Если у вас есть вопросы или предложения:
1. Создайте [Issue](https://github.com/dildebekvaas/flight-service-kg/issues)
2. Напишите на email: your-email@example.com
3. Присоединяйтесь к обсуждению в [Discussions](https://github.com/dildebekvaas/flight-service-kg/discussions)

---

⭐ Поставьте звезду если проект вам понравился!

🚀 **[Демо версия](https://yourusername.pythonanywhere.com)** | 📚 **[Документация](docs/)** | 🐛 **[Сообщить об ошибке](https://github.com/dildebekvaas/flight-service-kg/issues)**