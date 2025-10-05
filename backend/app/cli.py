import click
from flask.cli import with_appcontext
from flask import current_app
from . import db
from .models import User, Company, Flight, Ticket, Banner, Offer
from datetime import datetime, timedelta

@click.command()
@with_appcontext
def init_db():
    """Initialize the database."""
    db.create_all()
    click.echo('Initialized the database.')

@click.command()
@with_appcontext
def drop_db():
    """Drop all database tables."""
    db.drop_all()
    click.echo('Dropped all tables.')

@click.command()
@with_appcontext
def reset_db():
    """Reset the database (drop and recreate)."""
    db.drop_all()
    db.create_all()
    click.echo('Reset the database.')

@click.command()
@with_appcontext
def seed_db():
    """Seed the database with sample data."""
    # Check if data already exists
    if User.query.count() > 0:
        click.echo('Database already contains data. Use reset-db first.')
        return
    
    from app import initialize_sample_data
    initialize_sample_data()
    click.echo('Seeded the database with sample data.')

@click.command()
@click.argument('email')
@click.argument('password')
@click.option('--name', default='Admin User', help='Admin user name')
@with_appcontext
def create_admin(email, password, name):
    """Create an admin user."""
    # Check if user already exists
    if User.query.filter_by(email=email).first():
        click.echo(f'User with email {email} already exists.')
        return
    
    admin = User(
        name=name,
        email=email,
        role='admin',
        is_active=True
    )
    admin.set_password(password)
    
    db.session.add(admin)
    db.session.commit()
    
    click.echo(f'Created admin user: {email}')

@click.command()
@click.argument('company_name')
@click.argument('company_code')
@click.argument('manager_email')
@with_appcontext
def create_company(company_name, company_code, manager_email):
    """Create a new airline company."""
    # Check if manager exists
    manager = User.query.filter_by(email=manager_email, role='company_manager').first()
    if not manager:
        click.echo(f'Company manager with email {manager_email} not found.')
        return
    
    # Check if company code already exists
    if Company.query.filter_by(code=company_code.upper()).first():
        click.echo(f'Company with code {company_code} already exists.')
        return
    
    company = Company(
        name=company_name,
        code=company_code.upper(),
        manager_id=manager.id,
        is_active=True
    )
    
    db.session.add(company)
    db.session.commit()
    
    click.echo(f'Created company: {company_name} ({company_code})')

@click.command()
@with_appcontext
def cleanup_past_flights():
    """Remove flights that departed more than 30 days ago."""
    cutoff_date = datetime.utcnow() - timedelta(days=30)
    
    # Find old flights
    old_flights = Flight.query.filter(Flight.depart_time < cutoff_date).all()
    
    count = 0
    for flight in old_flights:
        # Only delete if no tickets exist
        if not flight.tickets:
            db.session.delete(flight)
            count += 1
    
    db.session.commit()
    click.echo(f'Cleaned up {count} old flights.')

@click.command()
@with_appcontext
def stats():
    """Show database statistics."""
    users = User.query.count()
    companies = Company.query.count()
    flights = Flight.query.count()
    tickets = Ticket.query.count()
    
    active_flights = Flight.query.filter(Flight.depart_time > datetime.utcnow()).count()
    paid_tickets = Ticket.query.filter_by(status='paid').count()
    
    click.echo('Database Statistics:')
    click.echo(f'Users: {users}')
    click.echo(f'Companies: {companies}')
    click.echo(f'Flights: {flights} (Active: {active_flights})')
    click.echo(f'Tickets: {tickets} (Paid: {paid_tickets})')

def init_app(app):
    """Register CLI commands with the Flask application."""
    app.cli.add_command(init_db)
    app.cli.add_command(drop_db)
    app.cli.add_command(reset_db)
    app.cli.add_command(seed_db)
    app.cli.add_command(create_admin)
    app.cli.add_command(create_company)
    app.cli.add_command(cleanup_past_flights)
    app.cli.add_command(stats)