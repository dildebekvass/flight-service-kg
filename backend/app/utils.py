from datetime import datetime, timedelta
from flask import flash
import re

def format_currency(amount):
    """Format currency for display"""
    return f"${amount:.2f}"

def format_duration(depart_time, arrive_time):
    """Format flight duration"""
    delta = arrive_time - depart_time
    hours, remainder = divmod(delta.total_seconds(), 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{int(hours)}h {int(minutes)}m"

def format_datetime(dt):
    """Format datetime for display"""
    return dt.strftime("%Y-%m-%d %H:%M")

def format_date(dt):
    """Format date for display"""
    return dt.strftime("%Y-%m-%d")

def format_time(dt):
    """Format time for display"""
    return dt.strftime("%H:%M")

def validate_flight_number(flight_number):
    """Validate flight number format (e.g., AA123, BA456)"""
    pattern = r'^[A-Z]{2,3}[0-9]{1,4}$'
    return bool(re.match(pattern, flight_number.upper()))

def validate_airport_code(code):
    """Validate airport code format (3 letters)"""
    pattern = r'^[A-Z]{3}$'
    return bool(re.match(pattern, code.upper()))

def calculate_refund_amount(ticket):
    """Calculate refund amount based on cancellation policy"""
    if not ticket.can_be_refunded:
        return 0
    
    # Simple refund policy - full refund if 24+ hours before departure
    time_diff = ticket.flight.depart_time - datetime.utcnow()
    
    if time_diff.total_seconds() > 24 * 3600:  # 24+ hours
        return ticket.price
    elif time_diff.total_seconds() > 2 * 3600:  # 2-24 hours
        return ticket.price * 0.5  # 50% refund
    else:
        return 0  # No refund

def generate_seat_number():
    """Generate a random seat number"""
    import random
    row = random.randint(1, 30)
    seat = random.choice(['A', 'B', 'C', 'D', 'E', 'F'])
    return f"{row}{seat}"

def flash_errors(form):
    """Flash form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Error in {getattr(form, field).label.text}: {error}", 'danger')

def get_time_filter_dates(filter_type):
    """Get date range for time filters"""
    now = datetime.utcnow()
    
    if filter_type == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
    elif filter_type == 'week':
        start_date = now - timedelta(days=7)
        end_date = now
    elif filter_type == 'month':
        start_date = now - timedelta(days=30)
        end_date = now
    else:  # 'all'
        start_date = None
        end_date = None
    
    return start_date, end_date

def paginate_query(query, page, per_page=20):
    """Paginate a SQLAlchemy query"""
    return query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

def is_safe_url(target):
    """Check if redirect URL is safe"""
    from urllib.parse import urlparse, urljoin
    from flask import request
    
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def allowed_file(filename, allowed_extensions=None):
    """Check if uploaded file has allowed extension"""
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def calculate_flight_statistics(flights):
    """Calculate statistics for a list of flights"""
    now = datetime.utcnow()
    
    total_flights = len(flights)
    active_flights = len([f for f in flights if f.depart_time > now])
    completed_flights = total_flights - active_flights
    
    total_passengers = sum(len([t for t in f.tickets if t.status == 'paid']) for f in flights)
    total_revenue = sum(sum(t.price for t in f.tickets if t.status == 'paid') for f in flights)
    
    return {
        'total_flights': total_flights,
        'active_flights': active_flights,
        'completed_flights': completed_flights,
        'total_passengers': total_passengers,
        'total_revenue': total_revenue
    }