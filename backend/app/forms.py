from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, IntegerField, FloatField, DateTimeField, SelectField, TextAreaField, BooleanField, HiddenField, DateField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, ValidationError
from .models import User, Company
from datetime import datetime

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class RegisterForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=4)])
    submit = SubmitField('Зарегистрироваться')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Пользователь с таким email уже зарегистрирован. Выберите другой email или попробуйте войти в систему.')

class FlightSearchForm(FlaskForm):
    origin = StringField('Откуда', validators=[Optional()])
    destination = StringField('Куда', validators=[Optional()])
    depart_date = DateTimeField('Дата отправления', format='%Y-%m-%d', validators=[Optional()])
    passengers = IntegerField('Пассажиры', default=1, validators=[Optional(), NumberRange(min=1, max=10)])
    submit = SubmitField('Найти рейсы')

class FlightForm(FlaskForm):
    flight_number = StringField('Номер рейса', validators=[DataRequired(), Length(min=2, max=20)])
    origin = StringField('Место отправления', validators=[DataRequired(), Length(max=80)])
    destination = StringField('Место назначения', validators=[DataRequired(), Length(max=80)])
    # Remove datetime fields validation - handle manually
    price = FloatField('Цена', validators=[DataRequired(), NumberRange(min=0)])
    seats_total = IntegerField('Всего мест', validators=[DataRequired(), NumberRange(min=1, max=1000)])
    stops = IntegerField('Количество пересадок', default=0, validators=[NumberRange(min=0, max=5)])
    aircraft_type = StringField('Тип самолета', validators=[Optional(), Length(max=50)])
    submit = SubmitField('Сохранить рейс')

class TicketPurchaseForm(FlaskForm):
    passenger_name = StringField('Имя пассажира', validators=[DataRequired(), Length(min=2, max=120)])
    submit = SubmitField('Купить билет')

class CompanyForm(FlaskForm):
    name = StringField('Название компании', validators=[DataRequired(), Length(min=2, max=140)])
    code = StringField('Код авиакомпании', validators=[DataRequired(), Length(min=2, max=10)])
    manager_id = SelectField('Менеджер', coerce=int, validators=[Optional()])
    is_active = BooleanField('Активна', default=True)
    submit = SubmitField('Сохранить компанию')
    
    def __init__(self, *args, **kwargs):
        super(CompanyForm, self).__init__(*args, **kwargs)
        # Populate manager choices with company managers
        managers = User.query.filter_by(role='company_manager').all()
        self.manager_id.choices = [(0, 'Выберите менеджера')] + [(m.id, f"{m.name} ({m.email})") for m in managers]

class UserManagementForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[Optional(), Length(min=6)])
    role = SelectField('Роль', choices=[
        ('user', 'Обычный пользователь'),
        ('company_manager', 'Менеджер компании'),
        ('admin', 'Администратор')
    ], validators=[DataRequired()])
    is_active = BooleanField('Активен', default=True)
    submit = SubmitField('Сохранить пользователя')

class BannerForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired(), Length(min=2, max=200)])
    description = TextAreaField('Описание', validators=[Optional()])
    image_url = StringField('URL изображения', validators=[Optional(), Length(max=500)])
    link_url = StringField('URL ссылки', validators=[Optional(), Length(max=500)])
    is_active = BooleanField('Активен', default=True)
    order = IntegerField('Порядок отображения', default=0, validators=[NumberRange(min=0)])
    submit = SubmitField('Сохранить баннер')

class OfferForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired(), Length(min=2, max=200)])
    description = TextAreaField('Описание', validators=[Optional()])
    discount_percentage = FloatField('Скидка %', validators=[NumberRange(min=0, max=100)])
    valid_from = DateTimeField('Действительно с', format='%Y-%m-%d', validators=[DataRequired()])
    valid_to = DateTimeField('Действительно до', format='%Y-%m-%d', validators=[DataRequired()])
    promo_code = StringField('Промо-код', validators=[Optional(), Length(max=50)])
    is_active = BooleanField('Активен', default=True)
    submit = SubmitField('Сохранить предложение')
    
    def validate_valid_to(self, field):
        if field.data <= self.valid_from.data:
            raise ValidationError('Дата окончания должна быть после даты начала.')

class FlightFilterForm(FlaskForm):
    min_price = FloatField('Мин. цена', validators=[Optional(), NumberRange(min=0)])
    max_price = FloatField('Макс. цена', validators=[Optional(), NumberRange(min=0)])
    airline = SelectField('Авиакомпания', coerce=int, validators=[Optional()])
    max_stops = SelectField('Макс. пересадок', choices=[
        ('', 'Любое'),
        ('0', 'Прямой'),
        ('1', '1 пересадка'),
        ('2', '2+ пересадки')
    ], validators=[Optional()])
    sort_by = SelectField('Сортировать по', choices=[
        ('price_asc', 'Цене (по возрастанию)'),
        ('price_desc', 'Цене (по убыванию)'),
        ('depart_time', 'Времени отправления'),
        ('duration', 'Продолжительности')
    ], default='price_asc')
    submit = SubmitField('Применить фильтры')
    
    def __init__(self, *args, **kwargs):
        super(FlightFilterForm, self).__init__(*args, **kwargs)
        # Populate airline choices
        companies = Company.query.filter_by(is_active=True).all()
        self.airline.choices = [(0, 'Любая авиакомпания')] + [(c.id, c.name) for c in companies]

class ConfirmationSearchForm(FlaskForm):
    confirmation_id = StringField('ID подтверждения', validators=[DataRequired(), Length(min=1, max=50)])
    submit = SubmitField('Найти билет')

class ProfileForm(FlaskForm):
    name = StringField('Полное имя', validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Телефон', validators=[Optional(), Length(max=20)])
    birth_date = DateField('Дата рождения', validators=[Optional()])
    passport_number = StringField('Номер паспорта', validators=[Optional(), Length(max=50)])
    address = TextAreaField('Адрес', validators=[Optional(), Length(max=500)])
    nationality = StringField('Гражданство', validators=[Optional(), Length(max=50)])
    bio = TextAreaField('О себе', validators=[Optional(), Length(max=1000)])
    avatar = FileField('Фото профиля', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Только изображения!')])
    submit = SubmitField('Сохранить профиль')
    
    def __init__(self, original_email, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.original_email = original_email
    
    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Этот email уже используется другим пользователем.')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Текущий пароль', validators=[DataRequired()])
    new_password = PasswordField('Новый пароль', validators=[DataRequired(), Length(min=4)])
    confirm_password = PasswordField('Подтвердите новый пароль', validators=[DataRequired(), Length(min=4)])
    submit = SubmitField('Изменить пароль')
    
    def validate_confirm_password(self, confirm_password):
        if confirm_password.data != self.new_password.data:
            raise ValidationError('Пароли не совпадают.')
