from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, make_response, current_app
from . import db
from .models import User, Company, Flight, Ticket, Banner, Offer
from .forms import (LoginForm, RegisterForm, FlightForm, FlightSearchForm, 
                   FlightFilterForm, TicketPurchaseForm, CompanyForm, 
                   UserManagementForm, BannerForm, OfferForm, ConfirmationSearchForm,
                   ProfileForm, ChangePasswordForm)
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from werkzeug.utils import secure_filename
import io
import base64
import qrcode
import os
import uuid

# Helper function for file uploads
def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    """Save uploaded file and return URL"""
    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(current_app.static_folder, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # Return URL path
        return f"/static/uploads/{unique_filename}"
    return None

bp = Blueprint('main', __name__)

# ============== PUBLIC ROUTES ==============

@bp.route('/')
def index():
    """Landing page with search and banners"""
    search_form = FlightSearchForm()
    banners = Banner.query.filter_by(is_active=True).order_by(Banner.order).all()
    offers = Offer.query.filter(
        and_(Offer.is_active == True, 
             Offer.valid_from <= datetime.utcnow(),
             or_(Offer.valid_to.is_(None), Offer.valid_to >= datetime.utcnow()))
    ).limit(3).all()
    
    flights = []
    all_flights = []
    
    # Get search results if search parameters provided
    if request.args.get('origin') or request.args.get('destination') or request.args.get('depart_date'):
        flights = search_flights_query()
    
    # Always get all available flights for browsing
    all_flights = Flight.query.filter(
        Flight.depart_time > datetime.utcnow(),
        Flight.seats_available > 0
    ).order_by(Flight.depart_time.asc()).limit(20).all()
    
    return render_template('index.html', 
                         search_form=search_form, 
                         banners=banners, 
                         offers=offers, 
                         flights=flights,
                         all_flights=all_flights)

def search_flights_query():
    """Helper function to search flights based on query parameters"""
    origin = request.args.get('origin', '')
    destination = request.args.get('destination', '')
    depart_date = request.args.get('depart_date')
    passengers = int(request.args.get('passengers', 1))
    
    # Base query for available flights in the future
    query = Flight.query.filter(
        Flight.depart_time > datetime.utcnow(),
        Flight.seats_available >= passengers
    )
    
    # Apply search filters
    if origin:
        query = query.filter(Flight.origin.ilike(f"%{origin}%"))
    if destination:
        query = query.filter(Flight.destination.ilike(f"%{destination}%"))
    if depart_date:
        try:
            date_obj = datetime.strptime(depart_date, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Flight.depart_time) == date_obj)
        except ValueError:
            pass
    
    return query.order_by(Flight.depart_time.asc()).all()

@bp.route('/search')
def search_flights():
    """Simple flight search - only origin and destination"""
    origin = request.args.get('origin', '').strip()
    destination = request.args.get('destination', '').strip()
    
    # Base query for available flights in the future
    query = Flight.query.filter(Flight.depart_time > datetime.utcnow())
    
    # Apply search filters
    if origin:
        query = query.filter(Flight.origin.ilike(f"%{origin}%"))
    if destination:
        query = query.filter(Flight.destination.ilike(f"%{destination}%"))
    
    # Order by departure time
    flights = query.order_by(Flight.depart_time.asc()).all()
    
    return render_template('search_results.html', 
                         flights=flights, 
                         search_params=request.args,
                         origin=origin,
                         destination=destination)

@bp.route('/flight/<int:flight_id>')
def flight_details(flight_id):
    """View detailed flight information"""
    flight = Flight.query.get_or_404(flight_id)
    return render_template('flight_details.html', flight=flight)

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        # Дополнительная проверка на существующий email
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            form.email.errors.append('Пользователь с таким email уже зарегистрирован. Попробуйте войти в систему или используйте другой email.')
            return render_template('signup.html', form=form)
        
        user = User(
            name=form.name.data, 
            email=form.email.data, 
            role='user'
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            flash('Регистрация успешна! Теперь вы можете войти в систему.', 'success')
            return redirect(url_for('main.login'))
            
        except Exception as e:
            db.session.rollback()
            # Дополнительная проверка на конфликт email в базе данных
            if 'UNIQUE constraint failed: user.email' in str(e):
                form.email.errors.append('Пользователь с таким email уже зарегистрирован. Попробуйте войти в систему или используйте другой email.')
            else:
                flash('Ошибка при регистрации. Попробуйте еще раз.', 'danger')
            return render_template('signup.html', form=form)
        
    return render_template('signup.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Ваш аккаунт деактивирован. Обратитесь в службу поддержки.', 'danger')
                return render_template('login.html', form=form)
            
            login_user(user)
            flash(f'Добро пожаловать, {user.name}!', 'success')
            
            # Redirect based on user role
            if user.is_admin():
                return redirect(url_for('main.admin_panel'))
            elif user.is_company_manager():
                return redirect(url_for('main.company_dashboard'))
            else:
                return redirect(url_for('main.dashboard'))
        flash('Неверный email или пароль.', 'danger')
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('main.index'))

# ============== USER DASHBOARD ==============

@bp.route('/dashboard')
@login_required
def dashboard():
    """Regular user dashboard"""
    if not current_user.is_regular_user():
        flash('Доступ запрещен.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get user's tickets
    tickets = Ticket.query.filter_by(user_id=current_user.id).order_by(Ticket.created_at.desc()).all()
    
    # Get upcoming flights for schedule view
    upcoming_flights = []
    for ticket in tickets:
        if ticket.status == 'paid' and ticket.flight.is_upcoming:
            upcoming_flights.append(ticket.flight)
    
    search_form = FlightSearchForm()
    filter_form = FlightFilterForm()
    
    return render_template('dashboard.html', 
                         tickets=tickets, 
                         upcoming_flights=upcoming_flights,
                         search_form=search_form,
                         filter_form=filter_form)

@bp.route('/buy/<int:flight_id>', methods=['GET', 'POST'])
@login_required
def buy_ticket(flight_id):
    """Purchase a ticket for a flight"""
    if not current_user.is_regular_user():
        flash('Только обычные пользователи могут покупать билеты.', 'danger')
        return redirect(url_for('main.index'))
    
    flight = Flight.query.get_or_404(flight_id)
    
    if flight.seats_available <= 0:
        flash('На этом рейсе нет свободных мест.', 'danger')
        return redirect(url_for('main.flight_details', flight_id=flight_id))
    
    if not flight.is_upcoming:
        flash('Нельзя бронировать прошедшие рейсы.', 'danger')
        return redirect(url_for('main.flight_details', flight_id=flight_id))
    
    form = TicketPurchaseForm()
    if form.validate_on_submit():
        # Create ticket
        ticket = Ticket(
            user_id=current_user.id,
            flight_id=flight.id,
            price=flight.price,
            passenger_name=form.passenger_name.data,
            status='pending_payment'  # Изменено на ожидание оплаты
        )
        
        # Update available seats
        flight.seats_available -= 1
        
        db.session.add(ticket)
        db.session.commit()
        
        # Детальное сообщение об успешном бронировании
        flash(f'''✅ Билет успешно забронирован! 
        
📋 Номер подтверждения: {ticket.confirmation_id}
✈️ Рейс: {flight.flight_number}
💰 К оплате: {flight.price:.0f} сом

🔔 ВАЖНО: Пожалуйста, произведите оплату через QR-код в течение 24 часов.
В комментарии к переводу обязательно укажите номер рейса {flight.flight_number}.

После поступления оплаты ваш билет будет автоматически подтвержден.''', 'success')
        
        return redirect(url_for('main.dashboard'))
    
    return render_template('ticket_purchase.html', form=form, flight=flight)

@bp.route('/confirm_payment/<ticket_id>')
@login_required
def confirm_payment(ticket_id):
    if current_user.role != 'admin':
        flash('Недостаточно прав для выполнения этого действия.', 'error')
        return redirect(url_for('main.dashboard'))
    
    ticket = Ticket.query.get_or_404(ticket_id)
    if ticket.status == 'pending_payment':
        ticket.status = 'paid'
        db.session.commit()
        flash(f'Оплата билета {ticket.confirmation_id} подтверждена.', 'success')
    
    return redirect(url_for('main.dashboard'))

@bp.route('/mark_as_paid/<ticket_id>')
@login_required
def mark_as_paid(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    # Проверяем, что это билет текущего пользователя
    if ticket.user_id != current_user.id:
        flash('У вас нет прав для изменения этого билета.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if ticket.status == 'pending_payment':
        ticket.status = 'paid'
        db.session.commit()
        flash(f'Билет {ticket.confirmation_id} отмечен как оплаченный. Ожидайте подтверждения администратора.', 'success')
    else:
        flash('Этот билет уже оплачен или не требует оплаты.', 'info')
    
    return redirect(url_for('main.dashboard'))

@bp.route('/cancel_ticket/<int:ticket_id>')
@login_required
def cancel_ticket(ticket_id):
    """Cancel a ticket"""
    ticket = Ticket.query.get_or_404(ticket_id)
    
    # Check ownership or admin privilege
    if ticket.user_id != current_user.id and not current_user.is_admin():
        flash('Доступ запрещен.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if ticket.status != 'paid':
        flash('Билет уже отменен или возмещен.', 'warning')
        return redirect(url_for('main.dashboard'))
    
    # Check 24-hour rule
    if ticket.can_be_refunded:
        ticket.status = 'refunded'
        ticket.flight.seats_available += 1
        flash(f'Билет возмещен успешно. Сумма: {ticket.price:.2f} сом', 'success')
    else:
        ticket.status = 'canceled'
        flash('Билет отменен. Возмещение недоступно (менее 24 часов до вылета).', 'warning')
    
    ticket.canceled_at = datetime.utcnow()
    db.session.commit()
    
    return redirect(url_for('main.dashboard'))

@bp.route('/ticket/<confirmation_id>')
def view_ticket(confirmation_id):
    """View ticket by confirmation ID"""
    ticket = Ticket.query.filter_by(confirmation_id=confirmation_id.upper()).first_or_404()
    return render_template('ticket_view.html', ticket=ticket)

@bp.route('/search_ticket', methods=['GET', 'POST'])
def search_ticket():
    """Search for ticket by confirmation ID"""
    form = ConfirmationSearchForm()
    ticket = None
    
    if form.validate_on_submit():
        ticket = Ticket.query.filter_by(confirmation_id=form.confirmation_id.data.upper()).first()
        if not ticket:
            flash('Билет не найден.', 'danger')
    
    return render_template('search_ticket.html', form=form, ticket=ticket)

# ============== COMPANY MANAGEMENT ==============

@bp.route('/company/dashboard')
@login_required
def company_dashboard():
    """Company manager dashboard"""
    if not current_user.is_company_manager():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    company = Company.query.filter_by(manager_id=current_user.id).first()
    if not company:
        flash('No company assigned to your account.', 'warning')
        return redirect(url_for('main.index'))
    
    # Get flights and statistics
    flights = Flight.query.filter_by(company_id=company.id).order_by(Flight.depart_time.desc()).all()
    
    # Get time filter from request
    time_filter = request.args.get('filter', 'all')
    stats = company.get_statistics(time_filter)
    
    return render_template('company_dashboard.html', 
                         company=company,
                         flights=flights, 
                         stats=stats,
                         time_filter=time_filter)

@bp.route('/company/flight/new', methods=['GET', 'POST'])
@login_required
def company_new_flight():
    """Create new flight"""
    if not current_user.is_company_manager():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    company = Company.query.filter_by(manager_id=current_user.id).first()
    if not company:
        flash('No company assigned.', 'warning')
        return redirect(url_for('main.index'))
    
    form = FlightForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        # Parse datetime from datetime-local input
        from datetime import datetime
        
        # Get raw datetime strings from form
        depart_str = request.form.get('depart_time')
        arrive_str = request.form.get('arrive_time')
        
        errors = []
        
        # Validate datetime fields
        if not depart_str:
            errors.append('Departure time is required.')
        if not arrive_str:
            errors.append('Arrival time is required.')
        
        if not errors:
            try:
                # Parse datetime-local format (YYYY-MM-DDTHH:MM)
                depart_time = datetime.strptime(depart_str, '%Y-%m-%dT%H:%M')
                arrive_time = datetime.strptime(arrive_str, '%Y-%m-%dT%H:%M')
                
                # Validate business logic
                if depart_time <= datetime.now():
                    errors.append('Departure time must be in the future.')
                if arrive_time <= depart_time:
                    errors.append('Arrival time must be after departure time.')
                
            except ValueError:
                errors.append('Invalid date/time format.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
        else:
            flight = Flight(
                flight_number=form.flight_number.data,
                company_id=company.id,
                origin=form.origin.data,
                destination=form.destination.data,
                depart_time=depart_time,
                arrive_time=arrive_time,
                price=form.price.data,
                seats_total=form.seats_total.data,
                seats_available=form.seats_total.data,
                stops=form.stops.data,
                aircraft_type=form.aircraft_type.data
            )
            db.session.add(flight)
            db.session.commit()
            flash('Flight created successfully!', 'success')
            return redirect(url_for('main.company_dashboard'))
    
    return render_template('flight_form.html', form=form, title='Create New Flight')

@bp.route('/company/flight/<int:flight_id>/edit', methods=['GET', 'POST'])
@login_required
def company_edit_flight(flight_id):
    """Edit existing flight"""
    if not current_user.is_company_manager():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    company = Company.query.filter_by(manager_id=current_user.id).first()
    if not company:
        flash('No company assigned.', 'warning')
        return redirect(url_for('main.index'))
    
    flight = Flight.query.filter_by(id=flight_id, company_id=company.id).first_or_404()
    
    form = FlightForm(obj=flight)
    
    if request.method == 'POST' and form.validate_on_submit():
        # Parse datetime from datetime-local input
        from datetime import datetime
        
        # Get raw datetime strings from form
        depart_str = request.form.get('depart_time')
        arrive_str = request.form.get('arrive_time')
        
        errors = []
        
        # Validate datetime fields
        if not depart_str:
            errors.append('Departure time is required.')
        if not arrive_str:
            errors.append('Arrival time is required.')
        
        if not errors:
            try:
                # Parse datetime-local format (YYYY-MM-DDTHH:MM)
                depart_time = datetime.strptime(depart_str, '%Y-%m-%dT%H:%M')
                arrive_time = datetime.strptime(arrive_str, '%Y-%m-%dT%H:%M')
                
                # Validate business logic
                if depart_time <= datetime.now():
                    errors.append('Departure time must be in the future.')
                if arrive_time <= depart_time:
                    errors.append('Arrival time must be after departure time.')
                
            except ValueError:
                errors.append('Invalid date/time format.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
        else:
            # Update flight object
            flight.flight_number = form.flight_number.data
            flight.origin = form.origin.data
            flight.destination = form.destination.data
            flight.depart_time = depart_time
            flight.arrive_time = arrive_time
            flight.price = form.price.data
            flight.seats_total = form.seats_total.data
            flight.stops = form.stops.data
            flight.aircraft_type = form.aircraft_type.data
            
            db.session.commit()
            flash('Flight updated successfully!', 'success')
            return redirect(url_for('main.company_dashboard'))
    
    return render_template('flight_form.html', form=form, title='Edit Flight', flight=flight)

@bp.route('/company/flight/<int:flight_id>/delete')
@login_required
def company_delete_flight(flight_id):
    """Delete flight"""
    if not current_user.is_company_manager():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    company = Company.query.filter_by(manager_id=current_user.id).first()
    if not company:
        flash('No company assigned.', 'warning')
        return redirect(url_for('main.index'))
    
    flight = Flight.query.filter_by(id=flight_id, company_id=company.id).first_or_404()
    
    # Check if flight has booked tickets
    if flight.tickets:
        flash('Cannot delete flight with existing bookings.', 'danger')
        return redirect(url_for('main.company_dashboard'))
    
    db.session.delete(flight)
    db.session.commit()
    flash('Flight deleted successfully!', 'success')
    return redirect(url_for('main.company_dashboard'))

@bp.route('/company/flight/<int:flight_id>/passengers')
@login_required
def company_flight_passengers(flight_id):
    """View passengers for a flight"""
    if not current_user.is_company_manager():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    company = Company.query.filter_by(manager_id=current_user.id).first()
    if not company:
        flash('No company assigned.', 'warning')
        return redirect(url_for('main.index'))
    
    flight = Flight.query.filter_by(id=flight_id, company_id=company.id).first_or_404()
    passengers = flight.get_passengers()
    
    return render_template('flight_passengers.html', flight=flight, passengers=passengers)

# ============== PROFILE ==============

@bp.route('/profile')
@login_required
def profile():
    """Просмотр профиля пользователя"""
    # Вычисляем статистику билетов
    from app.models import Ticket
    
    total_tickets = Ticket.query.filter_by(user_id=current_user.id).count()
    paid_tickets = Ticket.query.filter_by(user_id=current_user.id, status='paid').count()
    pending_tickets = Ticket.query.filter_by(user_id=current_user.id, status='pending_payment').count()
    cancelled_tickets = Ticket.query.filter_by(user_id=current_user.id, status='cancelled').count()
    
    ticket_stats = {
        'total': total_tickets,
        'paid': paid_tickets,
        'pending': pending_tickets,
        'cancelled': cancelled_tickets
    }
    
    return render_template('profile.html', user=current_user, ticket_stats=ticket_stats)

@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Редактирование профиля пользователя"""
    form = ProfileForm(current_user.email)
    
    if form.validate_on_submit():
        try:
            # Обновляем основную информацию
            current_user.name = form.name.data
            current_user.email = form.email.data
            current_user.phone = form.phone.data
            current_user.birth_date = form.birth_date.data
            current_user.passport_number = form.passport_number.data
            current_user.address = form.address.data
            current_user.nationality = form.nationality.data
            current_user.bio = form.bio.data
            
            # Обработка загрузки аватара
            if form.avatar.data:
                import os
                import uuid
                from werkzeug.utils import secure_filename
                
                # Создаем папку для загрузок если не существует
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'avatars')
                os.makedirs(upload_folder, exist_ok=True)
                
                # Генерируем уникальное имя файла
                filename = secure_filename(form.avatar.data.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                filepath = os.path.join(upload_folder, unique_filename)
                
                # Удаляем старый аватар если есть
                if current_user.avatar_filename:
                    old_filepath = os.path.join(upload_folder, current_user.avatar_filename)
                    if os.path.exists(old_filepath):
                        os.remove(old_filepath)
                
                # Сохраняем новый аватар
                form.avatar.data.save(filepath)
                current_user.avatar_filename = unique_filename
            
            db.session.commit()
            flash('Профиль успешно обновлен!', 'success')
            return redirect(url_for('main.profile'))
            
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при обновлении профиля. Попробуйте еще раз.', 'danger')
            
    elif request.method == 'GET':
        # Заполняем форму текущими данными
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.phone.data = current_user.phone
        form.birth_date.data = current_user.birth_date
        form.passport_number.data = current_user.passport_number
        form.address.data = current_user.address
        form.nationality.data = current_user.nationality
        form.bio.data = current_user.bio
    
    return render_template('edit_profile.html', form=form)

@bp.route('/profile/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Смена пароля"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Пароль успешно изменен!', 'success')
            return redirect(url_for('main.profile'))
        else:
            flash('Неверный текущий пароль.', 'danger')
    
    return render_template('change_password.html', form=form)

# ============== ADMIN PANEL ==============

@bp.route('/admin')
@login_required
def admin_panel():
    """Admin dashboard with time filtering"""
    if not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get time filter
    time_filter = request.args.get('filter', 'all')
    
    # Base queries
    users = User.query.all()
    companies = Company.query.all()
    
    # Apply time filter to flights
    flight_query = Flight.query
    now = datetime.utcnow()
    
    if time_filter == 'today':
        today = now.date()
        flight_query = flight_query.filter(db.func.date(Flight.depart_time) == today)
    elif time_filter == 'week':
        week_ago = now - timedelta(days=7)
        flight_query = flight_query.filter(Flight.depart_time >= week_ago)
    elif time_filter == 'month':
        month_ago = now - timedelta(days=30)
        flight_query = flight_query.filter(Flight.depart_time >= month_ago)
    
    flights = flight_query.all()
    
    # Calculate filtered statistics
    total_flights = len(flights)
    active_flights = len([f for f in flights if f.depart_time > now])
    completed_flights = len([f for f in flights if f.depart_time <= now])
    
    # Calculate passengers and revenue for filtered flights
    total_passengers = 0
    total_revenue = 0.0
    
    for flight in flights:
        paid_tickets = [t for t in flight.tickets if t.status == 'paid']
        total_passengers += len(paid_tickets)
        total_revenue += sum(t.price for t in paid_tickets)
    
    # Additional statistics (always show all-time data)
    all_flights = Flight.query.all()
    active_users = User.query.filter_by(is_active=True).count()
    active_companies = Company.query.filter_by(is_active=True).count()
    
    stats = {
        'total_flights': total_flights,
        'active_flights': active_flights,
        'completed_flights': completed_flights,
        'total_passengers': total_passengers,
        'total_revenue': total_revenue,
        'total_users': len(users),
        'active_users': active_users,
        'total_companies': len(companies),
        'active_companies': active_companies,
        'all_time_flights': len(all_flights),
        'all_time_revenue': sum(sum(t.price for t in f.tickets if t.status == 'paid') for f in all_flights)
    }
    
    return render_template('admin.html', 
                         users=users, 
                         companies=companies,
                         stats=stats,
                         time_filter=time_filter)

@bp.route('/admin/users')
@login_required
def admin_users():
    """User management"""
    if not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@bp.route('/admin/user/<int:user_id>/toggle_status')
@login_required
def admin_toggle_user_status(user_id):
    """Block/unblock user"""
    if not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Cannot deactivate your own account.', 'danger')
        return redirect(url_for('main.admin_users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.name} has been {status}.', 'success')
    return redirect(url_for('main.admin_users'))

@bp.route('/admin/user/new', methods=['GET', 'POST'])
@login_required
def admin_new_user():
    """Create new user"""
    if not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    form = UserManagementForm()
    
    if form.validate_on_submit():
        # Check if email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('A user with this email already exists.', 'danger')
        elif not form.password.data:
            flash('Password is required for new users.', 'danger')
        else:
            user = User(
                name=form.name.data,
                email=form.email.data,
                role=form.role.data,
                is_active=form.is_active.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash(f'User {user.name} created successfully!', 'success')
            return redirect(url_for('main.admin_users'))
    
    return render_template('user_form.html', form=form, title='Create New User')

@bp.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    """Edit existing user"""
    if not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    form = UserManagementForm(obj=user)
    
    if form.validate_on_submit():
        # Check if email conflicts with another user
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user and existing_user.id != user.id:
            flash('A user with this email already exists.', 'danger')
        else:
            user.name = form.name.data
            user.email = form.email.data
            user.role = form.role.data
            user.is_active = form.is_active.data
            
            # Update password only if provided
            if form.password.data:
                user.set_password(form.password.data)
            
            db.session.commit()
            flash(f'User {user.name} updated successfully!', 'success')
            return redirect(url_for('main.admin_users'))
    
    return render_template('user_form.html', form=form, title='Edit User', user=user)

@bp.route('/admin/companies')
@login_required
def admin_companies():
    """Company management"""
    if not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    companies = Company.query.all()
    return render_template('admin_companies.html', companies=companies)

@bp.route('/admin/company/new', methods=['GET', 'POST'])
@login_required
def admin_new_company():
    """Create new company"""
    if not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    form = CompanyForm()
    if form.validate_on_submit():
        company = Company(
            name=form.name.data,
            code=form.code.data.upper()
        )
        if form.manager_id.data and form.manager_id.data != 0:
            company.manager_id = form.manager_id.data
        
        db.session.add(company)
        db.session.commit()
        flash('Company created successfully!', 'success')
        return redirect(url_for('main.admin_companies'))
    
    return render_template('company_form.html', form=form, title='Create New Company')

@bp.route('/admin/company/<int:company_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_company(company_id):
    """Edit company"""
    if not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    company = Company.query.get_or_404(company_id)
    form = CompanyForm(obj=company)
    
    if form.validate_on_submit():
        form.populate_obj(company)
        if form.manager_id.data == 0:
            company.manager_id = None
        db.session.commit()
        flash('Company updated successfully!', 'success')
        return redirect(url_for('main.admin_companies'))
    
    return render_template('company_form.html', form=form, title='Edit Company')

@bp.route('/admin/company/<int:company_id>/toggle_status')
@login_required
def admin_toggle_company_status(company_id):
    """Activate/deactivate company"""
    if not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    company = Company.query.get_or_404(company_id)
    company.is_active = not company.is_active
    db.session.commit()
    
    status = 'activated' if company.is_active else 'deactivated'
    flash(f'Company {company.name} has been {status}.', 'success')
    return redirect(url_for('main.admin_companies'))

@bp.route('/admin/content')
@login_required
def admin_content():
    """Content management - banners and offers"""
    if not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    banners = Banner.query.order_by(Banner.order).all()
    offers = Offer.query.order_by(Offer.created_at.desc()).all()
    
    return render_template('admin_content.html', banners=banners, offers=offers)

@bp.route('/admin/content', methods=['POST'])
@login_required
def admin_content_post():
    """Handle content management form submissions"""
    if not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    action = request.form.get('action')
    
    if action == 'banner':
        banner_id = request.form.get('banner_id')
        if banner_id:  # Edit existing banner
            banner = Banner.query.get_or_404(banner_id)
        else:  # Create new banner
            banner = Banner()
        
        banner.title = request.form.get('title')
        
        # Handle image upload or URL
        image_file = request.files.get('image_file')
        image_url = request.form.get('image_url')
        
        if image_file and image_file.filename:
            # File uploaded - save it and use the URL
            uploaded_url = save_uploaded_file(image_file)
            if uploaded_url:
                banner.image_url = uploaded_url
                flash('Изображение успешно загружено!', 'success')
            else:
                flash('Ошибка загрузки изображения. Проверьте формат файла.', 'danger')
                return redirect(url_for('main.admin_content'))
        elif image_url:
            # URL provided - use it
            banner.image_url = image_url
        
        banner.is_active = 'is_active' in request.form
        
        if not banner_id:
            db.session.add(banner)
        
        db.session.commit()
        flash('Banner saved successfully!', 'success')
    
    elif action == 'offer':
        offer_id = request.form.get('offer_id')
        if offer_id:  # Edit existing offer
            offer = Offer.query.get_or_404(offer_id)
        else:  # Create new offer
            offer = Offer()
        
        offer.title = request.form.get('title')
        offer.description = request.form.get('description')
        offer.discount_percent = int(request.form.get('discount_percent', 0))
        
        valid_until_str = request.form.get('valid_until')
        if valid_until_str:
            try:
                offer.valid_until = datetime.strptime(valid_until_str, '%Y-%m-%d')
            except ValueError:
                offer.valid_until = None
        else:
            offer.valid_until = None
        
        offer.is_active = 'is_active' in request.form
        
        if not offer_id:
            db.session.add(offer)
        
        db.session.commit()
        flash('Offer saved successfully!', 'success')
    
    return redirect(url_for('main.admin_content'))

@bp.route('/admin/banner/<int:banner_id>/toggle_status')
@login_required
def admin_toggle_banner_status(banner_id):
    """Toggle banner active status"""
    if not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    banner = Banner.query.get_or_404(banner_id)
    banner.is_active = not banner.is_active
    db.session.commit()
    
    status = 'activated' if banner.is_active else 'deactivated'
    flash(f'Banner "{banner.title}" has been {status}.', 'success')
    return redirect(url_for('main.admin_content'))

@bp.route('/admin/offer/<int:offer_id>/toggle_status')
@login_required
def admin_toggle_offer_status(offer_id):
    """Toggle offer active status"""
    if not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    offer = Offer.query.get_or_404(offer_id)
    offer.is_active = not offer.is_active
    db.session.commit()
    
    status = 'activated' if offer.is_active else 'deactivated'
    flash(f'Offer "{offer.title}" has been {status}.', 'success')
    return redirect(url_for('main.admin_content'))

@bp.route('/admin/banner/new', methods=['GET', 'POST'])
@login_required
def admin_new_banner():
    """Create new banner"""
    if not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    form = BannerForm()
    if form.validate_on_submit():
        banner = Banner()
        form.populate_obj(banner)
        db.session.add(banner)
        db.session.commit()
        flash('Banner created successfully!', 'success')
        return redirect(url_for('main.admin_content'))
    
    return render_template('banner_form.html', form=form, title='Create New Banner')

@bp.route('/admin/offer/new', methods=['GET', 'POST'])
@login_required
def admin_new_offer():
    """Create new offer"""
    if not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    form = OfferForm()
    if form.validate_on_submit():
        offer = Offer()
        form.populate_obj(offer)
        db.session.add(offer)
        db.session.commit()
        flash('Offer created successfully!', 'success')
        return redirect(url_for('main.admin_content'))
    
    return render_template('offer_form.html', form=form, title='Create New Offer')

# ============== API ENDPOINTS ==============

@bp.route('/api/flights')
def api_flights():
    """API endpoint for flight search"""
    flights = Flight.query.filter(Flight.depart_time > datetime.utcnow()).all()
    return jsonify([{
        'id': f.id,
        'flight_number': f.flight_number,
        'origin': f.origin,
        'destination': f.destination,
        'depart_time': f.depart_time.isoformat(),
        'arrive_time': f.arrive_time.isoformat(),
        'price': f.price,
        'seats_available': f.seats_available,
        'company': f.company.name if f.company else None
    } for f in flights])

# ============== ERROR HANDLERS ==============

@bp.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
