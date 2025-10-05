# Flight Ticketing Web Service

A comprehensive web application for flight booking and management with support for users, airline companies, and administrators.

## Features

### For Users
- Search and filter flights by origin, destination, date, price, airline, and stops
- View detailed flight information
- Purchase tickets with simple checkout process
- View purchased tickets and flight schedules
- Cancel tickets with automatic refund calculation (24-hour rule)
- Search tickets by confirmation ID

### For Airline Companies
- Company dashboard with flight management
- Add, edit, and delete flights
- Set seat availability and pricing
- View passenger lists for flights
- Comprehensive statistics with time filters (today, week, month, all time)
- Revenue tracking and performance metrics

### For Administrators
- User management (view, block/unblock users)
- Company management (create, edit, deactivate companies)
- Assign company managers
- Content management (banners and promotional offers)
- System-wide statistics and analytics
- Time-filtered reporting

### Additional Features
- Responsive design for all devices
- RESTful API for mobile app integration
- Advanced search with filters and sorting
- Promotional banners and offers system
- Automatic seat availability management
- Flight status tracking
- Template filters for data formatting

## Technology Stack

### Backend
- **Flask** - Web framework
- **SQLAlchemy** - ORM and database management
- **Flask-Login** - User session management
- **Flask-WTF** - Form handling and CSRF protection
- **Flask-Migrate** - Database migrations
- **SQLite** - Database (easily replaceable with PostgreSQL/MySQL)

### Security Features
- Password hashing with Werkzeug
- CSRF protection on all forms
- Session management
- Role-based access control
- Input validation and sanitization

## Installation and Setup

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Step 1: Clone and Navigate
```bash
cd backend
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration
Copy the example environment file:
```bash
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux
```

Edit `.env` file with your configuration:
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///flight_service.db
```

### Step 5: Initialize Database

#### Option A: Quick Start with Sample Data
```bash
python seed_db.py
```

#### Option B: Manual Setup
```bash
flask init-db
flask seed-db
```

### Step 6: Run the Application
```bash
python run.py
```

The application will be available at: `http://127.0.0.1:5000`

## Test Accounts

After seeding the database, you can use these test accounts:

### Admin Account
- **Email:** admin@flightservice.com
- **Password:** admin123
- **Access:** Full system administration

### Company Manager Accounts
- **Email:** john@skyways.com
- **Password:** manager123
- **Company:** Skyways Airlines

- **Email:** sarah@blueair.com  
- **Password:** manager123
- **Company:** Blue Air Express

### Regular User Accounts
- **Email:** alice@example.com
- **Password:** user123

- **Email:** bob@example.com
- **Password:** user123

## Database Management Commands

The application includes several CLI commands for database management:

```bash
# Initialize empty database
flask init-db

# Drop all tables
flask drop-db

# Reset database (drop and recreate)
flask reset-db

# Seed with sample data
flask seed-db

# Create admin user
flask create-admin admin@example.com password123 --name "Admin User"

# Create company
flask create-company "New Airline" "NEW" manager@example.com

# Clean up old flights
flask cleanup-past-flights

# Show database statistics
flask stats
```

## API Endpoints

The application provides a RESTful API for mobile app integration:

### Public Endpoints
- `GET /api/flights` - Search flights with filters
- `GET /api/flights/<id>` - Get flight details
- `GET /api/airlines` - Get list of airlines
- `GET /api/tickets/<confirmation_id>` - Get ticket by confirmation
- `GET /api/search/suggestions` - Get search suggestions
- `GET /api/stats` - Get public statistics

### Authenticated Endpoints
- `GET /api/tickets` - Get user's tickets
- `POST /api/tickets/<id>/cancel` - Cancel ticket

### Example API Usage
```bash
# Search flights
curl "http://localhost:5000/api/flights?origin=New%20York&destination=Los%20Angeles&depart_date=2024-12-25"

# Get flight details
curl "http://localhost:5000/api/flights/1"

# Get ticket by confirmation
curl "http://localhost:5000/api/tickets/ABC12345"
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py          # App factory and initialization
│   ├── models.py            # Database models
│   ├── routes.py            # Web routes and views
│   ├── forms.py             # WTForms for user input
│   ├── api.py               # RESTful API endpoints
│   ├── utils.py             # Utility functions
│   ├── filters.py           # Template filters
│   ├── cli.py               # CLI commands
│   ├── static/              # Static files (CSS, JS, images)
│   └── templates/           # Jinja2 templates
├── config.py                # Configuration settings
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
├── seed_db.py              # Database seeding script
└── .env.example            # Environment variables example
```

## Database Schema

### Users Table
- id, name, email, password_hash, role, is_active, created_at
- Roles: 'user', 'company_manager', 'admin'

### Companies Table
- id, name, code, manager_id, is_active, created_at

### Flights Table
- id, flight_number, company_id, origin, destination
- depart_time, arrive_time, price, seats_total, seats_available
- stops, aircraft_type, created_at

### Tickets Table
- id, user_id, flight_id, confirmation_id, price, passenger_name
- seat_number, status, created_at, canceled_at

### Banners & Offers Tables
- Support for promotional content and special offers

## Configuration

### Environment Variables
- `FLASK_ENV` - development/production
- `SECRET_KEY` - Flask secret key
- `DATABASE_URL` - Database connection string
- `MAIL_SERVER` - Email server for notifications (future)

### Application Settings
- `FLIGHTS_PER_PAGE` - Pagination for flight listings
- `TICKETS_PER_PAGE` - Pagination for ticket listings
- `MAX_CONTENT_LENGTH` - Maximum file upload size

## Security Features

1. **Password Security**: Passwords are hashed using Werkzeug's secure methods
2. **CSRF Protection**: All forms protected against cross-site request forgery
3. **Session Security**: Secure session management with Flask-Login
4. **Input Validation**: Comprehensive form validation with WTForms
5. **Role-Based Access**: Different permission levels for users, managers, and admins
6. **SQL Injection Prevention**: Using SQLAlchemy ORM with parameterized queries

## Business Logic

### Ticket Cancellation Policy
- **24+ hours before departure**: Full refund
- **Less than 24 hours**: No refund
- Canceled tickets free up seats for rebooking

### Flight Management
- Only company managers can manage their own company's flights
- Flights with existing bookings cannot be deleted
- Seat availability automatically updated on booking/cancellation

### User Roles and Permissions
- **Regular Users**: Book tickets, view their bookings, cancel tickets
- **Company Managers**: Manage flights, view passenger lists, access statistics
- **Administrators**: Full system access, user management, content management

## Testing

To run the application with test data:

1. Run the seeding script: `python seed_db.py`
2. Start the server: `python run.py`
3. Navigate to `http://127.0.0.1:5000`
4. Use test accounts to explore different roles

## Production Deployment

For production deployment:

1. Set `FLASK_ENV=production`
2. Use a production database (PostgreSQL recommended)
3. Set a strong `SECRET_KEY`
4. Configure proper logging
5. Use a production WSGI server (Gunicorn, uWSGI)
6. Set up reverse proxy (Nginx)
7. Enable HTTPS

## Future Enhancements

- Email notifications for booking confirmations
- Mobile push notifications
- Payment gateway integration
- Flight tracking and real-time updates
- Loyalty program with points system
- Multi-language support
- Advanced reporting and analytics
- Social media integration

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Examine the sample data and test accounts
4. Check application logs for error details

## License

This project is for demonstration purposes. Please ensure compliance with relevant regulations when deploying in production.
