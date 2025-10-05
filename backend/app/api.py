from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from . import db
from .models import Flight, Ticket, Company, User
from datetime import datetime
import json

api = Blueprint('api', __name__, url_prefix='/api')

# Helper function for JSON serialization
def serialize_flight(flight):
    """Serialize a flight object to JSON"""
    return {
        'id': flight.id,
        'flight_number': flight.flight_number,
        'company': {
            'id': flight.company.id,
            'name': flight.company.name,
            'code': flight.company.code
        } if flight.company else None,
        'origin': flight.origin,
        'destination': flight.destination,
        'depart_time': flight.depart_time.isoformat(),
        'arrive_time': flight.arrive_time.isoformat(),
        'duration': flight.duration,
        'price': flight.price,
        'seats_total': flight.seats_total,
        'seats_available': flight.seats_available,
        'stops': flight.stops,
        'aircraft_type': flight.aircraft_type,
        'is_upcoming': flight.is_upcoming
    }

def serialize_ticket(ticket):
    """Serialize a ticket object to JSON"""
    return {
        'id': ticket.id,
        'confirmation_id': ticket.confirmation_id,
        'flight': serialize_flight(ticket.flight),
        'passenger_name': ticket.passenger_name,
        'seat_number': ticket.seat_number,
        'price': ticket.price,
        'status': ticket.status,
        'created_at': ticket.created_at.isoformat(),
        'can_be_refunded': ticket.can_be_refunded
    }

@api.route('/flights')
def get_flights():
    """Get list of available flights with optional filtering"""
    try:
        # Get query parameters
        origin = request.args.get('origin', '').strip()
        destination = request.args.get('destination', '').strip()
        depart_date = request.args.get('depart_date', '').strip()
        passengers = int(request.args.get('passengers', 1))
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        airline_id = request.args.get('airline_id', type=int)
        max_stops = request.args.get('max_stops', type=int)
        sort_by = request.args.get('sort_by', 'price_asc')
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100 results
        
        # Base query for future flights with available seats
        query = Flight.query.filter(
            Flight.depart_time > datetime.utcnow(),
            Flight.seats_available >= passengers
        )
        
        # Apply filters
        if origin:
            query = query.filter(Flight.origin.ilike(f'%{origin}%'))
        
        if destination:
            query = query.filter(Flight.destination.ilike(f'%{destination}%'))
        
        if depart_date:
            try:
                date_obj = datetime.strptime(depart_date, '%Y-%m-%d').date()
                query = query.filter(db.func.date(Flight.depart_time) == date_obj)
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        if min_price is not None:
            query = query.filter(Flight.price >= min_price)
        
        if max_price is not None:
            query = query.filter(Flight.price <= max_price)
        
        if airline_id is not None:
            query = query.filter(Flight.company_id == airline_id)
        
        if max_stops is not None:
            query = query.filter(Flight.stops <= max_stops)
        
        # Apply sorting
        if sort_by == 'price_asc':
            query = query.order_by(Flight.price.asc())
        elif sort_by == 'price_desc':
            query = query.order_by(Flight.price.desc())
        elif sort_by == 'depart_time':
            query = query.order_by(Flight.depart_time.asc())
        elif sort_by == 'duration':
            query = query.order_by((Flight.arrive_time - Flight.depart_time).asc())
        
        # Apply limit
        flights = query.limit(limit).all()
        
        return jsonify({
            'flights': [serialize_flight(flight) for flight in flights],
            'count': len(flights),
            'total_available': query.count()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/flights/<int:flight_id>')
def get_flight(flight_id):
    """Get detailed information about a specific flight"""
    flight = Flight.query.get_or_404(flight_id)
    return jsonify({'flight': serialize_flight(flight)})

@api.route('/airlines')
def get_airlines():
    """Get list of all airlines"""
    companies = Company.query.filter_by(is_active=True).all()
    return jsonify({
        'airlines': [{
            'id': company.id,
            'name': company.name,
            'code': company.code
        } for company in companies]
    })

@api.route('/tickets', methods=['GET'])
@login_required
def get_user_tickets():
    """Get current user's tickets"""
    if not current_user.is_regular_user():
        return jsonify({'error': 'Access denied'}), 403
    
    tickets = Ticket.query.filter_by(user_id=current_user.id).order_by(Ticket.created_at.desc()).all()
    
    return jsonify({
        'tickets': [serialize_ticket(ticket) for ticket in tickets],
        'count': len(tickets)
    })

@api.route('/tickets/<confirmation_id>')
def get_ticket_by_confirmation(confirmation_id):
    """Get ticket details by confirmation ID"""
    ticket = Ticket.query.filter_by(confirmation_id=confirmation_id.upper()).first()
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    return jsonify({'ticket': serialize_ticket(ticket)})

@api.route('/tickets/<int:ticket_id>/cancel', methods=['POST'])
@login_required
def cancel_ticket_api(ticket_id):
    """Cancel a ticket via API"""
    ticket = Ticket.query.get_or_404(ticket_id)
    
    # Check ownership or admin privilege
    if ticket.user_id != current_user.id and not current_user.is_admin():
        return jsonify({'error': 'Access denied'}), 403
    
    if ticket.status != 'paid':
        return jsonify({'error': 'Ticket is already canceled or refunded'}), 400
    
    # Check 24-hour rule
    if ticket.can_be_refunded:
        ticket.status = 'refunded'
        ticket.flight.seats_available += 1
        refund_amount = ticket.price
        message = f'Ticket refunded successfully. Amount: ${refund_amount:.2f}'
    else:
        ticket.status = 'canceled'
        refund_amount = 0
        message = 'Ticket canceled. No refund available (less than 24 hours before departure).'
    
    ticket.canceled_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': message,
        'refund_amount': refund_amount,
        'ticket': serialize_ticket(ticket)
    })

@api.route('/search/suggestions')
def get_search_suggestions():
    """Get search suggestions for airports/cities"""
    query = request.args.get('q', '').strip()
    type_filter = request.args.get('type', 'all')  # 'origin', 'destination', 'all'
    
    if len(query) < 2:
        return jsonify({'suggestions': []})
    
    # Get unique origins and destinations
    suggestions = set()
    
    if type_filter in ['origin', 'all']:
        origins = db.session.query(Flight.origin).filter(
            Flight.origin.ilike(f'%{query}%')
        ).distinct().limit(10).all()
        suggestions.update([origin[0] for origin in origins])
    
    if type_filter in ['destination', 'all']:
        destinations = db.session.query(Flight.destination).filter(
            Flight.destination.ilike(f'%{query}%')
        ).distinct().limit(10).all()
        suggestions.update([dest[0] for dest in destinations])
    
    return jsonify({
        'suggestions': sorted(list(suggestions))[:10]
    })

@api.route('/stats')
def get_public_stats():
    """Get public statistics"""
    total_flights = Flight.query.count()
    active_flights = Flight.query.filter(Flight.depart_time > datetime.utcnow()).count()
    total_airlines = Company.query.filter_by(is_active=True).count()
    
    return jsonify({
        'total_flights': total_flights,
        'active_flights': active_flights,
        'total_airlines': total_airlines
    })

# Error handlers for API
@api.errorhandler(404)
def api_not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@api.errorhandler(400)
def api_bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@api.errorhandler(500)
def api_internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500