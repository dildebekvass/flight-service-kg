from . import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import uuid
from sqlalchemy import and_, or_

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(30), default='user')  # user, company_manager, admin
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Profile fields
    phone = db.Column(db.String(20), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    passport_number = db.Column(db.String(50), nullable=True)
    address = db.Column(db.Text, nullable=True)
    nationality = db.Column(db.String(50), nullable=True)
    avatar_filename = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = db.relationship('Company', backref='manager', uselist=False, foreign_keys='Company.manager_id')

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)

    def is_admin(self):
        return self.role == 'admin'
    
    def is_company_manager(self):
        return self.role == 'company_manager'
    
    def is_regular_user(self):
        return self.role == 'user'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)  # Airline code like "AA", "UA"
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    flights = db.relationship('Flight', backref='company', lazy=True)

    def get_statistics(self, time_filter='all'):
        """Get company statistics with time filtering"""
        from datetime import datetime, timedelta
        
        base_query = Flight.query.filter_by(company_id=self.id)
        now = datetime.utcnow()
        
        # Apply time filter to departure time
        if time_filter == 'today':
            today = now.date()
            query = base_query.filter(db.func.date(Flight.depart_time) == today)
        elif time_filter == 'week':
            week_ago = now - timedelta(days=7)
            query = base_query.filter(Flight.depart_time >= week_ago)
        elif time_filter == 'month':
            month_ago = now - timedelta(days=30)
            query = base_query.filter(Flight.depart_time >= month_ago)
        else:  # 'all' time
            query = base_query
        
        flights = query.all()
        
        # Calculate statistics
        total_flights = len(flights)
        active_flights = len([f for f in flights if f.depart_time > now])
        completed_flights = len([f for f in flights if f.depart_time <= now])
        
        # Count passengers and revenue (only paid tickets)
        total_passengers = 0
        total_revenue = 0.0
        
        for flight in flights:
            paid_tickets = [t for t in flight.tickets if t.status == 'paid']
            total_passengers += len(paid_tickets)
            total_revenue += sum(t.price for t in paid_tickets)
        
        return {
            'total_flights': total_flights,
            'active_flights': active_flights,
            'completed_flights': completed_flights,
            'total_passengers': total_passengers,
            'total_revenue': total_revenue
        }

class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(20), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    origin = db.Column(db.String(80), nullable=False)
    destination = db.Column(db.String(80), nullable=False)
    depart_time = db.Column(db.DateTime, nullable=False)
    arrive_time = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)
    seats_total = db.Column(db.Integer, default=100)
    seats_available = db.Column(db.Integer, default=100)
    stops = db.Column(db.Integer, default=0)  # Number of stops/layovers
    aircraft_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tickets = db.relationship('Ticket', backref='flight', lazy=True)

    @property
    def duration(self):
        """Flight duration in hours and minutes"""
        delta = self.arrive_time - self.depart_time
        hours, remainder = divmod(delta.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{int(hours)}h {int(minutes)}m"

    @property
    def seats_booked(self):
        """Number of seats currently booked (paid tickets only)"""
        return len([t for t in self.tickets if t.status == 'paid'])
    
    @property
    def is_full(self):
        """Check if flight is fully booked"""
        return self.seats_available <= 0
    
    @property
    def is_upcoming(self):
        """Check if flight is in the future"""
        return self.depart_time > datetime.utcnow()
    
    def get_passengers(self):
        """Get list of passengers with paid tickets"""
        return [t.user for t in self.tickets if t.status == 'paid']

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=False)
    status = db.Column(db.String(30), default='pending_payment')  # pending_payment, paid, refunded, canceled
    confirmation_id = db.Column(db.String(50), unique=True, default=lambda: str(uuid.uuid4())[:8].upper())
    price = db.Column(db.Float, nullable=False)
    passenger_name = db.Column(db.String(120))  # Can be different from user name
    seat_number = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    canceled_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', backref='tickets')
    
    @property
    def can_be_refunded(self):
        """Check if ticket can be refunded (24+ hours before departure)"""
        if self.status != 'paid':
            return False
        time_diff = self.flight.depart_time - datetime.utcnow()
        return time_diff.total_seconds() > 24 * 3600  # 24 hours
    
    @property
    def refund_amount(self):
        """Calculate refund amount based on cancellation time"""
        if self.can_be_refunded:
            return self.price
        return 0

class Banner(db.Model):
    """Landing page banners for promotions"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    link_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Offer(db.Model):
    """Special offers and promotions"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    discount_percentage = db.Column(db.Float, default=0)
    valid_from = db.Column(db.DateTime, default=datetime.utcnow)
    valid_to = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    promo_code = db.Column(db.String(50), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
