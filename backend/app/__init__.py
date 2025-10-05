import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from datetime import datetime, timedelta

# Загружаем переменные окружения из .env файла
from dotenv import load_dotenv
load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_name=None):
    app = Flask(__name__, static_folder='static', template_folder='templates')
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Import config
    from config import config
    app.config.from_object(config[config_name])
    
    # Override with environment variables if set
    if os.environ.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    if os.environ.get('DATABASE_URL'):
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    if os.environ.get('APP_URL'):
        app.config['APP_URL'] = os.environ.get('APP_URL')
    
    # Mail configuration for development
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD') 
    app.config['MAIL_DEFAULT_SENDER'] = 'noreply@flightservice.kg'
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    migrate.init_app(app, db)

    # Register template filters
    from .filters import register_template_filters
    register_template_filters(app)

    # Register blueprints
    from . import routes
    from .api import api
    app.register_blueprint(routes.bp)
    app.register_blueprint(api)

    # Register CLI commands
    from . import cli
    cli.init_app(app)

    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Initialize sample data if database is empty
        # Temporarily disabled to avoid database issues during development
        # initialize_sample_data()

    return app

def initialize_sample_data():
    """Initialize the database with sample data for testing"""
    from .models import User, Company, Flight, Banner, Offer
    
    try:
        # Check if we already have data
        if User.query.count() > 0:
            return
    except Exception as e:
        print(f"Error checking database: {e}")
        return
    
    print("Initializing sample data...")
    
    # Create users
    admin = User(
        name='System Administrator',
        email='admin@example.com',
        role='admin',
        is_active=True
    )
    admin.set_password('password')
    
    # Company managers
    manager1 = User(
        name='John Smith',
        email='john@skyways.com',
        role='company_manager',
        is_active=True
    )
    manager1.set_password('password')
    
    manager2 = User(
        name='Sarah Johnson',
        email='sarah@blueair.com',
        role='company_manager',
        is_active=True
    )
    manager2.set_password('password')
    
    # Regular users
    user1 = User(
        name='Alice Cooper',
        email='alice@example.com',
        role='user',
        is_active=True
    )
    user1.set_password('password')
    
    user2 = User(
        name='Bob Wilson',
        email='bob@example.com',
        role='user',
        is_active=True
    )
    user2.set_password('password')
    
    db.session.add_all([admin, manager1, manager2, user1, user2])
    db.session.commit()
    
    # Create companies
    company1 = Company(
        name='Skyways Airlines',
        code='SKY',
        manager_id=manager1.id,
        is_active=True
    )
    
    company2 = Company(
        name='Blue Air Express',
        code='BLU',
        manager_id=manager2.id,
        is_active=True
    )
    
    db.session.add_all([company1, company2])
    db.session.commit()
    
    # Create sample flights
    base_time = datetime.utcnow() + timedelta(days=1)
    
    flights = [
        # Skyways Airlines flights
        Flight(
            flight_number='SKY101',
            company_id=company1.id,
            origin='New York (JFK)',
            destination='Los Angeles (LAX)',
            depart_time=base_time + timedelta(hours=8),
            arrive_time=base_time + timedelta(hours=14),
            price=299.99,
            seats_total=180,
            seats_available=180,
            stops=0,
            aircraft_type='Boeing 737'
        ),
        Flight(
            flight_number='SKY202',
            company_id=company1.id,
            origin='Los Angeles (LAX)',
            destination='Chicago (ORD)',
            depart_time=base_time + timedelta(days=1, hours=10),
            arrive_time=base_time + timedelta(days=1, hours=14),
            price=249.99,
            seats_total=160,
            seats_available=160,
            stops=0,
            aircraft_type='Airbus A320'
        ),
        Flight(
            flight_number='SKY303',
            company_id=company1.id,
            origin='Miami (MIA)',
            destination='New York (JFK)',
            depart_time=base_time + timedelta(days=2, hours=6),
            arrive_time=base_time + timedelta(days=2, hours=9),
            price=199.99,
            seats_total=140,
            seats_available=140,
            stops=0,
            aircraft_type='Boeing 737'
        ),
        
        # Blue Air Express flights
        Flight(
            flight_number='BLU401',
            company_id=company2.id,
            origin='Chicago (ORD)',
            destination='Miami (MIA)',
            depart_time=base_time + timedelta(hours=12),
            arrive_time=base_time + timedelta(hours=15, minutes=30),
            price=179.99,
            seats_total=120,
            seats_available=120,
            stops=0,
            aircraft_type='Embraer E-Jet'
        ),
        Flight(
            flight_number='BLU502',
            company_id=company2.id,
            origin='San Francisco (SFO)',
            destination='Seattle (SEA)',
            depart_time=base_time + timedelta(days=1, hours=16),
            arrive_time=base_time + timedelta(days=1, hours=18, minutes=30),
            price=149.99,
            seats_total=100,
            seats_available=100,
            stops=0,
            aircraft_type='Boeing 737'
        ),
        Flight(
            flight_number='BLU603',
            company_id=company2.id,
            origin='Boston (BOS)',
            destination='San Francisco (SFO)',
            depart_time=base_time + timedelta(days=3, hours=9),
            arrive_time=base_time + timedelta(days=3, hours=16),
            price=399.99,
            seats_total=180,
            seats_available=180,
            stops=1,
            aircraft_type='Airbus A321'
        ),
    ]
    
    db.session.add_all(flights)
    db.session.commit()
    
    # Create sample banners
    banners = [
        Banner(
            title='Welcome to Flight Service!',
            description='Book your next adventure with us. Best prices guaranteed!',
            image_url='/static/images/banner1.jpg',
            link_url='/',
            is_active=True,
            order=1
        ),
        Banner(
            title='Summer Sale - 25% Off!',
            description='Limited time offer on all domestic flights. Book now!',
            image_url='/static/images/banner2.jpg',
            link_url='/search',
            is_active=True,
            order=2
        ),
        Banner(
            title='Join Our Loyalty Program',
            description='Earn points with every flight and get exclusive discounts.',
            image_url='/static/images/banner3.jpg',
            link_url='/signup',
            is_active=True,
            order=3
        ),
    ]
    
    db.session.add_all(banners)
    db.session.commit()
    
    # Create sample offers
    offers = [
        Offer(
            title='Early Bird Special',
            description='Book 30 days in advance and save 20%',
            discount_percentage=20.0,
            valid_from=datetime.utcnow(),
            valid_to=datetime.utcnow() + timedelta(days=60),
            promo_code='EARLY20',
            is_active=True
        ),
        Offer(
            title='Weekend Getaway',
            description='Special weekend rates for short trips',
            discount_percentage=15.0,
            valid_from=datetime.utcnow(),
            valid_to=datetime.utcnow() + timedelta(days=30),
            promo_code='WEEKEND15',
            is_active=True
        ),
    ]
    
    db.session.add_all(offers)
    db.session.commit()
    
    print("Sample data initialized successfully!")
    print("\nTest Accounts:")
    print("Admin: admin@example.com / password")
    print("Company Manager 1: john@skyways.com / password")
    print("Company Manager 2: sarah@blueair.com / password")
    print("User 1: alice@example.com / password")
    print("User 2: bob@example.com / password")
