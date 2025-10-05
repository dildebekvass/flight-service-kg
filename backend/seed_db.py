#!/usr/bin/env python3
"""
Database seeding script for development and testing.
Run this script to populate the database with sample data.
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Company, Flight, Ticket, Banner, Offer
from datetime import datetime, timedelta
import random

def create_sample_users():
    """Create sample users with different roles"""
    users = []
    
    # Admin user
    admin = User(
        name='System Administrator',
        email='admin@flightservice.com',
        role='admin',
        is_active=True
    )
    admin.set_password('admin123')
    users.append(admin)
    
    # Company managers
    managers = [
        ('John Smith', 'john@skyways.com', 'Skyways Airlines'),
        ('Sarah Johnson', 'sarah@blueair.com', 'Blue Air Express'),
        ('Mike Wilson', 'mike@fastjets.com', 'Fast Jets'),
        ('Lisa Brown', 'lisa@cloudfly.com', 'CloudFly Airlines'),
    ]
    
    for name, email, company_name in managers:
        manager = User(
            name=name,
            email=email,
            role='company_manager',
            is_active=True
        )
        manager.set_password('manager123')
        users.append(manager)
    
    # Regular users
    regular_users = [
        ('Alice Cooper', 'alice@example.com'),
        ('Bob Wilson', 'bob@example.com'),
        ('Carol Davis', 'carol@example.com'),
        ('David Miller', 'david@example.com'),
        ('Emma Johnson', 'emma@example.com'),
        ('Frank Brown', 'frank@example.com'),
        ('Grace Lee', 'grace@example.com'),
        ('Henry Clark', 'henry@example.com'),
    ]
    
    for name, email in regular_users:
        user = User(
            name=name,
            email=email,
            role='user',
            is_active=True
        )
        user.set_password('user123')
        users.append(user)
    
    return users

def create_sample_companies():
    """Create sample airline companies"""
    companies_data = [
        ('Skyways Airlines', 'SKY'),
        ('Blue Air Express', 'BLU'),
        ('Fast Jets', 'FAST'),
        ('CloudFly Airlines', 'CLF'),
    ]
    
    companies = []
    managers = User.query.filter_by(role='company_manager').all()
    
    for i, (name, code) in enumerate(companies_data):
        company = Company(
            name=name,
            code=code,
            manager_id=managers[i].id if i < len(managers) else None,
            is_active=True
        )
        companies.append(company)
    
    return companies

def create_sample_flights():
    """Create sample flights with realistic data"""
    companies = Company.query.all()
    
    # Major US airports
    airports = [
        'New York (JFK)',
        'Los Angeles (LAX)',
        'Chicago (ORD)',
        'Miami (MIA)',
        'San Francisco (SFO)',
        'Seattle (SEA)',
        'Boston (BOS)',
        'Denver (DEN)',
        'Las Vegas (LAS)',
        'Dallas (DFW)',
        'Phoenix (PHX)',
        'Atlanta (ATL)',
    ]
    
    aircraft_types = [
        'Boeing 737',
        'Boeing 747',
        'Boeing 777',
        'Airbus A320',
        'Airbus A321',
        'Airbus A380',
        'Embraer E-Jet',
        'Bombardier CRJ',
    ]
    
    flights = []
    base_time = datetime.utcnow() + timedelta(hours=6)
    
    # Create flights for the next 30 days
    for day in range(30):
        current_date = base_time + timedelta(days=day)
        
        # Create 10-15 flights per day
        daily_flights = random.randint(10, 15)
        
        for _ in range(daily_flights):
            company = random.choice(companies)
            origin = random.choice(airports)
            destination = random.choice([a for a in airports if a != origin])
            
            # Random departure time during the day
            hour = random.randint(6, 22)
            minute = random.choice([0, 15, 30, 45])
            depart_time = current_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Flight duration (1-8 hours)
            duration_hours = random.randint(1, 8)
            duration_minutes = random.choice([0, 15, 30, 45])
            arrive_time = depart_time + timedelta(hours=duration_hours, minutes=duration_minutes)
            
            # Pricing based on distance/duration
            base_price = 100 + (duration_hours * 50) + random.randint(-50, 100)
            price = max(99.99, round(base_price, 2))
            
            # Seat configuration
            seats_total = random.choice([100, 120, 150, 180, 200, 250, 300])
            seats_available = random.randint(int(seats_total * 0.3), seats_total)
            
            # Flight number
            flight_num = random.randint(100, 999)
            flight_number = f"{company.code}{flight_num}"
            
            # Stops
            stops = random.choices([0, 1, 2], weights=[70, 25, 5])[0]
            
            flight = Flight(
                flight_number=flight_number,
                company_id=company.id,
                origin=origin,
                destination=destination,
                depart_time=depart_time,
                arrive_time=arrive_time,
                price=price,
                seats_total=seats_total,
                seats_available=seats_available,
                stops=stops,
                aircraft_type=random.choice(aircraft_types)
            )
            flights.append(flight)
    
    return flights

def create_sample_banners():
    """Create sample promotional banners"""
    banners = [
        Banner(
            title='Welcome to Flight Service!',
            description='Your trusted partner for all travel needs. Book now and save!',
            image_url='/static/images/banner1.jpg',
            link_url='/',
            is_active=True,
            order=1
        ),
        Banner(
            title='Summer Sale - Up to 30% Off!',
            description='Limited time offer on domestic and international flights.',
            image_url='/static/images/banner2.jpg',
            link_url='/search',
            is_active=True,
            order=2
        ),
        Banner(
            title='Join Our Loyalty Program',
            description='Earn points with every flight and unlock exclusive benefits.',
            image_url='/static/images/banner3.jpg',
            link_url='/signup',
            is_active=True,
            order=3
        ),
        Banner(
            title='Mobile App Coming Soon!',
            description='Book flights on the go with our upcoming mobile application.',
            image_url='/static/images/banner4.jpg',
            link_url='/',
            is_active=True,
            order=4
        ),
    ]
    return banners

def create_sample_offers():
    """Create sample promotional offers"""
    offers = [
        Offer(
            title='Early Bird Special',
            description='Book 30 days in advance and save 20% on all flights',
            discount_percentage=20.0,
            valid_from=datetime.utcnow(),
            valid_to=datetime.utcnow() + timedelta(days=90),
            promo_code='EARLY20',
            is_active=True
        ),
        Offer(
            title='Weekend Getaway',
            description='Special weekend rates for Friday-Sunday travels',
            discount_percentage=15.0,
            valid_from=datetime.utcnow(),
            valid_to=datetime.utcnow() + timedelta(days=60),
            promo_code='WEEKEND15',
            is_active=True
        ),
        Offer(
            title='Student Discount',
            description='Students save 10% on all domestic flights',
            discount_percentage=10.0,
            valid_from=datetime.utcnow(),
            valid_to=datetime.utcnow() + timedelta(days=365),
            promo_code='STUDENT10',
            is_active=True
        ),
        Offer(
            title='Holiday Special',
            description='Book your holiday travels with 25% discount',
            discount_percentage=25.0,
            valid_from=datetime.utcnow(),
            valid_to=datetime.utcnow() + timedelta(days=45),
            promo_code='HOLIDAY25',
            is_active=True
        ),
    ]
    return offers

def create_sample_tickets():
    """Create some sample tickets for testing"""
    users = User.query.filter_by(role='user').all()
    companies = Company.query.all()
    
    tickets = []
    
    # Create tickets for each company to ensure they all have some revenue
    for company in companies:
        company_flights = Flight.query.filter_by(company_id=company.id).limit(10).all()
        
        # Create 3-8 tickets per company
        num_tickets = random.randint(3, 8)
        
        for _ in range(num_tickets):
            if company_flights and users:
                user = random.choice(users)
                flight = random.choice(company_flights)
                
                # Make sure flight has available seats
                if flight.seats_available > 0:
                    ticket = Ticket(
                        user_id=user.id,
                        flight_id=flight.id,
                        price=flight.price,
                        passenger_name=user.name,
                        seat_number=f"{random.randint(1, 30)}{random.choice(['A', 'B', 'C', 'D', 'E', 'F'])}",
                        status='paid'
                    )
                    
                    # Reduce available seats
                    flight.seats_available -= 1
                    tickets.append(ticket)
    
    # Create additional random tickets
    all_flights = Flight.query.limit(50).all()
    for _ in range(20):  # Additional random tickets
        if all_flights and users:
            user = random.choice(users)
            flight = random.choice(all_flights)
            
            if flight.seats_available > 0:
                ticket = Ticket(
                    user_id=user.id,
                    flight_id=flight.id,
                    price=flight.price,
                    passenger_name=user.name,
                    seat_number=f"{random.randint(1, 30)}{random.choice(['A', 'B', 'C', 'D', 'E', 'F'])}",
                    status='paid'
                )
                
                flight.seats_available -= 1
                tickets.append(ticket)
    
    return tickets

def seed_database():
    """Main function to seed the database"""
    app = create_app()
    
    with app.app_context():
        print("Starting database seeding...")
        
        # Drop all tables and recreate
        print("Dropping existing tables...")
        db.drop_all()
        
        print("Creating tables...")
        db.create_all()
        
        # Create and add users
        print("Creating users...")
        users = create_sample_users()
        for user in users:
            db.session.add(user)
        db.session.commit()
        
        # Create and add companies
        print("Creating companies...")
        companies = create_sample_companies()
        for company in companies:
            db.session.add(company)
        db.session.commit()
        
        # Create and add flights
        print("Creating flights...")
        flights = create_sample_flights()
        for flight in flights:
            db.session.add(flight)
        db.session.commit()
        
        # Create and add banners
        print("Creating banners...")
        banners = create_sample_banners()
        for banner in banners:
            db.session.add(banner)
        db.session.commit()
        
        # Create and add offers
        print("Creating offers...")
        offers = create_sample_offers()
        for offer in offers:
            db.session.add(offer)
        db.session.commit()
        
        # Create and add tickets
        print("Creating sample tickets...")
        tickets = create_sample_tickets()
        for ticket in tickets:
            db.session.add(ticket)
        db.session.commit()
        
        print("\nDatabase seeding completed successfully!")
        
        # Print summary
        print(f"\nCreated:")
        print(f"- {len(users)} users")
        print(f"- {len(companies)} companies")
        print(f"- {len(flights)} flights")
        print(f"- {len(banners)} banners")
        print(f"- {len(offers)} offers")
        print(f"- {len(tickets)} tickets")
        
        print(f"\nTest Login Credentials:")
        print(f"Admin: admin@flightservice.com / admin123")
        print(f"Manager: john@skyways.com / manager123")
        print(f"User: alice@example.com / user123")

if __name__ == '__main__':
    seed_database()