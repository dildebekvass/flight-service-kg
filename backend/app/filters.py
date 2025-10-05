from flask import Blueprint
from datetime import datetime
from .utils import format_currency, format_duration, format_datetime, format_date, format_time

def register_template_filters(app):
    """Register custom template filters"""
    
    @app.template_filter('currency')
    def currency_filter(amount):
        """Format currency values"""
        if amount is None:
            return "$0.00"
        return format_currency(amount)
    
    @app.template_filter('datetime')
    def datetime_filter(dt):
        """Format datetime values"""
        if dt is None:
            return ""
        return format_datetime(dt)
    
    @app.template_filter('date')
    def date_filter(dt):
        """Format date values"""
        if dt is None:
            return ""
        return format_date(dt)
    
    @app.template_filter('time')
    def time_filter(dt):
        """Format time values"""
        if dt is None:
            return ""
        return format_time(dt)
    
    @app.template_filter('duration')
    def duration_filter(depart_time, arrive_time=None):
        """Format flight duration"""
        if arrive_time is None:
            # Assume depart_time is actually a timedelta
            delta = depart_time
            hours, remainder = divmod(delta.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{int(hours)}h {int(minutes)}m"
        return format_duration(depart_time, arrive_time)
    
    @app.template_filter('status_badge')
    def status_badge_filter(status):
        """Return Bootstrap badge class for status"""
        status_classes = {
            'paid': 'success',
            'refunded': 'info',
            'canceled': 'secondary',
            'active': 'success',
            'inactive': 'secondary'
        }
        return status_classes.get(status.lower(), 'secondary')
    
    @app.template_filter('capitalize_words')
    def capitalize_words_filter(text):
        """Capitalize each word in a string"""
        if not text:
            return ""
        return ' '.join(word.capitalize() for word in text.split())
    
    @app.template_filter('truncate_text')
    def truncate_text_filter(text, length=50, suffix='...'):
        """Truncate text to specified length"""
        if not text:
            return ""
        if len(text) <= length:
            return text
        return text[:length].rstrip() + suffix
    
    @app.template_filter('time_until')
    def time_until_filter(dt):
        """Show time remaining until a datetime"""
        if dt is None:
            return ""
        
        now = datetime.utcnow()
        if dt <= now:
            return "Past"
        
        delta = dt - now
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days} days, {hours} hours"
        elif hours > 0:
            return f"{hours} hours, {minutes} minutes"
        else:
            return f"{minutes} minutes"
    
    @app.template_filter('flight_status')
    def flight_status_filter(flight):
        """Determine flight status"""
        now = datetime.utcnow()
        
        if flight.depart_time > now:
            return "Scheduled"
        elif flight.depart_time <= now < flight.arrive_time:
            return "In Flight"
        else:
            return "Completed"
    
    @app.template_filter('seat_availability')
    def seat_availability_filter(flight):
        """Return seat availability text with color coding"""
        available = flight.seats_available
        total = flight.seats_total
        percentage = (available / total) * 100 if total > 0 else 0
        
        if percentage > 50:
            return f"{available} seats available"
        elif percentage > 10:
            return f"Only {available} seats left"
        elif available > 0:
            return f"Last {available} seats!"
        else:
            return "Sold out"