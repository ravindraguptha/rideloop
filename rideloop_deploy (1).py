#!/usr/bin/env python3
"""
RideLoop - Fully Functional Ride Sharing Platform
DEPLOYED VERSION - No distance-based pricing references
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import sqlite3

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'rideloop-secret-2024'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)
CORS(app)
jwt = JWTManager(app)

DB_PATH = 'rideloop.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        user_type TEXT DEFAULT 'passenger',
        vehicle_name TEXT,
        vehicle_type TEXT,
        vehicle_plate TEXT,
        rating REAL DEFAULT 5.0,
        trips INTEGER DEFAULT 0,
        latitude REAL,
        longitude REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS rides (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        driver_id INTEGER NOT NULL,
        driver_name TEXT NOT NULL,
        from_location TEXT NOT NULL,
        from_lat REAL,
        from_lng REAL,
        to_location TEXT NOT NULL,
        to_lat REAL,
        to_lng REAL,
        departure_time TEXT NOT NULL,
        available_seats INTEGER NOT NULL,
        booked_seats INTEGER DEFAULT 0,
        price_per_seat REAL NOT NULL,
        vehicle_type TEXT,
        vehicle_plate TEXT,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (driver_id) REFERENCES users(id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ride_id INTEGER NOT NULL,
        passenger_id INTEGER NOT NULL,
        driver_id INTEGER NOT NULL,
        num_passengers INTEGER NOT NULL,
        total_amount REAL NOT NULL,
        status TEXT DEFAULT 'confirmed',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (ride_id) REFERENCES rides(id),
        FOREIGN KEY (passenger_id) REFERENCES users(id),
        FOREIGN KEY (driver_id) REFERENCES users(id)
    )''')
    
    conn.commit()
    conn.close()

def insert_sample_data():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as count FROM users')
    if cursor.fetchone()['count'] > 0:
        conn.close()
        return
    
    users = [
        ('John Doe', '+91 98765 43210', 'john@rideloop.com', generate_password_hash('user123'), 'passenger'),
        ('Sarah Smith', '+91 87654 32109', 'sarah@rideloop.com', generate_password_hash('driver123'), 'driver'),
    ]
    
    user_ids = []
    for name, phone, email, pwd, utype in users:
        cursor.execute('''INSERT INTO users (name, phone, email, password, user_type) 
            VALUES (?, ?, ?, ?, ?)''', (name, phone, email, pwd, utype))
        user_ids.append(cursor.lastrowid)
    
    cursor.execute('''UPDATE users SET vehicle_name = ?, vehicle_type = ?, vehicle_plate = ? WHERE id = ?''',
                  ('Honda City', 'Sedan', 'DL-01-AB-1234', user_ids[1]))
    
    if len(user_ids) > 1:
        rides = [
            (user_ids[1], 'Sarah Smith', 'Delhi', 28.6139, 77.2090, 'Mumbai', 19.0760, 72.8777,
             (datetime.now() + timedelta(days=1, hours=6)).strftime('%Y-%m-%d %H:%M'), 4, 500),
            (user_ids[1], 'Sarah Smith', 'Bangalore', 12.9716, 77.5946, 'Hyderabad', 17.3850, 78.4867,
             (datetime.now() + timedelta(days=2, hours=8)).strftime('%Y-%m-%d %H:%M'), 6, 350),
        ]
        
        for d_id, d_name, from_loc, f_lat, f_lng, to_loc, t_lat, t_lng, time, seats, price in rides:
            cursor.execute('''INSERT INTO rides (driver_id, driver_name, from_location, from_lat, from_lng,
                to_location, to_lat, to_lng, departure_time, available_seats, price_per_seat, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')''',
                (d_id, d_name, from_loc, f_lat, f_lng, to_loc, t_lat, t_lng, time, seats, price))
    
    conn.commit()
    conn.close()

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        user_type = data.get('user_type', 'passenger')
        
        if not all([name, phone, email, password]):
            return jsonify({'error': 'All fields required'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE phone = ? OR email = ?', (phone, email))
        if cursor.fetchone():
            return jsonify({'error': 'Phone or email exists'}), 400
        
        cursor.execute('INSERT INTO users (name, phone, email, password, user_type) VALUES (?, ?, ?, ?, ?)',
                      (name, phone, email, generate_password_hash(password), user_type))
        conn.commit()
        
        cursor.execute('SELECT id, name, phone, user_type FROM users WHERE phone = ?', (phone,))
        user = dict(cursor.fetchone())
        conn.close()
        
        token = create_access_token(identity=user['id'])
        return jsonify({'user': user, 'token': token}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        phone = data.get('phone', '').strip()
        password = data.get('password', '').strip()
        
        if not phone or not password:
            return jsonify({'error': 'Phone and password required'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, phone, password, user_type FROM users WHERE phone = ?', (phone,))
        user_row = cursor.fetchone()
        conn.close()
        
        if not user_row or not check_password_hash(user_row['password'], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        user = {'id': user_row['id'], 'name': user_row['name'], 'phone': user_row['phone'], 'user_type': user_row['user_type']}
        token = create_access_token(identity=user['id'])
        return jsonify({'user': user, 'token': token}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''SELECT id, name, phone, email, user_type, vehicle_name, vehicle_type, 
                         vehicle_plate, rating, trips, latitude, longitude FROM users WHERE id = ?''', (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(dict(user)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        conn = get_db()
        cursor = conn.cursor()
        
        if 'vehicle_name' in data or 'vehicle_type' in data or 'vehicle_plate' in data:
            updates = []
            params = []
            
            if 'vehicle_name' in data:
                updates.append('vehicle_name = ?')
                params.append(data['vehicle_name'])
            if 'vehicle_type' in data:
                updates.append('vehicle_type = ?')
                params.append(data['vehicle_type'])
            if 'vehicle_plate' in data:
                updates.append('vehicle_plate = ?')
                params.append(data['vehicle_plate'])
            
            params.append(user_id)
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
        
        conn.commit()
        conn.close()
        return jsonify({'message': 'Profile updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/location', methods=['POST'])
@jwt_required()
def update_location():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        lat = data.get('latitude')
        lng = data.get('longitude')
        
        if lat is None or lng is None:
            return jsonify({'error': 'Location required'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET latitude = ?, longitude = ? WHERE id = ?', (lat, lng, user_id))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Location updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rides/create', methods=['POST'])
@jwt_required()
def create_ride():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT name, vehicle_type, vehicle_plate FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        from_loc = data.get('from_location')
        from_lat = data.get('from_lat')
        from_lng = data.get('from_lng')
        to_loc = data.get('to_location')
        to_lat = data.get('to_lat')
        to_lng = data.get('to_lng')
        time = data.get('departure_time')
        seats = data.get('available_seats', 4)
        price = float(data.get('price_per_seat', 0))
        
        if not all([from_loc, to_loc, time, price > 0]):
            return jsonify({'error': 'All fields required'}), 400
        
        cursor.execute('''INSERT INTO rides (driver_id, driver_name, from_location, from_lat, from_lng,
            to_location, to_lat, to_lng, departure_time, available_seats, price_per_seat, vehicle_type, vehicle_plate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (user_id, user['name'], from_loc, from_lat, from_lng, to_loc, to_lat, to_lng, time, seats, price, user['vehicle_type'], user['vehicle_plate']))
        
        conn.commit()
        ride_id = cursor.lastrowid
        conn.close()
        
        return jsonify({'message': 'Ride created', 'ride_id': ride_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rides/search', methods=['POST'])
def search_rides():
    try:
        data = request.get_json()
        from_loc = data.get('from_location', '').strip()
        to_loc = data.get('to_location', '').strip()
        passengers = data.get('passengers', 1)
        
        if not from_loc or not to_loc:
            return jsonify({'error': 'Locations required'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        query = '''SELECT id, driver_name, from_location, from_lat, from_lng,
                   to_location, to_lat, to_lng, departure_time, available_seats,
                   booked_seats, price_per_seat, vehicle_type, vehicle_plate, status
                   FROM rides WHERE status = 'active'
                   AND (available_seats - booked_seats) >= ?'''
        
        params = [passengers]
        
        if from_loc:
            query += ' AND from_location LIKE ?'
            params.append(f'%{from_loc}%')
        
        if to_loc:
            query += ' AND to_location LIKE ?'
            params.append(f'%{to_loc}%')
        
        query += ' ORDER BY departure_time ASC'
        
        cursor.execute(query, params)
        rides = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({'rides': rides}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bookings/create', methods=['POST'])
@jwt_required()
def create_booking():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        ride_id = data.get('ride_id')
        num_passengers = data.get('num_passengers', 1)
        
        if not ride_id or num_passengers < 1:
            return jsonify({'error': 'Invalid data'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''SELECT id, driver_id, available_seats, booked_seats, price_per_seat, status
                         FROM rides WHERE id = ?''', (ride_id,))
        
        ride = cursor.fetchone()
        
        if not ride:
            return jsonify({'error': 'Ride not found'}), 404
        
        if ride['status'] != 'active':
            return jsonify({'error': 'Ride not available'}), 400
        
        available = ride['available_seats'] - ride['booked_seats']
        if available < num_passengers:
            return jsonify({'error': f'Only {available} seats available'}), 400
        
        total = num_passengers * ride['price_per_seat']
        
        cursor.execute('''INSERT INTO bookings (ride_id, passenger_id, driver_id, num_passengers, total_amount)
                         VALUES (?, ?, ?, ?, ?)''',
                      (ride_id, user_id, ride['driver_id'], num_passengers, total))
        
        cursor.execute('UPDATE rides SET booked_seats = booked_seats + ? WHERE id = ?',
                      (num_passengers, ride_id))
        
        conn.commit()
        booking_id = cursor.lastrowid
        conn.close()
        
        return jsonify({'message': 'Booked!', 'booking_id': booking_id, 'total': total}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bookings', methods=['GET'])
@jwt_required()
def get_bookings():
    try:
        user_id = get_jwt_identity()
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''SELECT b.id, b.ride_id, r.from_location, r.to_location, r.departure_time,
                         b.num_passengers, b.total_amount, b.status, r.driver_name
                         FROM bookings b
                         JOIN rides r ON b.ride_id = r.id
                         WHERE b.passenger_id = ? ORDER BY r.departure_time DESC''', (user_id,))
        
        bookings = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({'bookings': bookings}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'OK'}), 200

FRONTEND_HTML = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RideLoop - Smart Ride Sharing</title>
<script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyDHn_8MZB_vPT9lJ_x7y_Y_lZ_H_Y_h_Y&libraries=places"></script>
<style>
* {margin: 0; padding: 0; box-sizing: border-box;}
body {font-family: 'DM Sans', -apple-system, sans-serif; background: #fafafa; color: #18181b;}
nav {position: fixed; top: 0; left: 0; right: 0; background: white; border-bottom: 1px solid #e4e4e7; 
     padding: 1rem 6%; display: flex; align-items: center; gap: 2rem; z-index: 999; height: 64px;}
.logo {display: flex; align-items: center; gap: 0.8rem; font-size: 1.45rem; font-weight: 700; cursor: pointer;}
.logo svg {width: 40px; height: 40px;}
.nav-links {display: flex; gap: 0.5rem; margin-left: auto;}
.nav-links button {background: none; border: none; padding: 0.4rem 0.85rem; cursor: pointer; font-size: 0.875rem; 
                   font-weight: 500; color: #52525b; border-radius: 100px; transition: all 0.2s;}
.nav-links button:hover {background: #e4e4e7; color: #18181b;}
.nav-cta {background: #18181b; color: white; padding: 0.5rem 1.25rem; border: none; border-radius: 100px; 
          font-weight: 600; cursor: pointer; margin-left: 0.5rem;}
.nav-cta:hover {background: #e8445a;}
.page {display: none; padding-top: 64px; min-height: 100vh;}
.page.on {display: block;}
.container {max-width: 600px; margin: 2rem auto; padding: 0 1rem;}
.modal {display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5);
         z-index: 1000; align-items: center; justify-content: center;}
.modal.on {display: flex;}
.modal-content {background: white; border-radius: 16px; padding: 2rem; width: 90%; max-width: 500px;
                max-height: 90vh; overflow-y: auto;}
.form-group {margin-bottom: 1.5rem;}
.form-label {display: block; font-weight: 600; margin-bottom: 0.5rem; font-size: 0.9rem;}
.form-input {width: 100%; padding: 0.75rem; border: 1.5px solid #e4e4e7; border-radius: 12px; font-size: 0.95rem;}
.form-input:focus {outline: none; border-color: #e8445a;}
.btn {width: 100%; padding: 0.8rem; background: #18181b; color: white; border: none; border-radius: 100px;
      font-weight: 600; cursor: pointer;}
.btn:hover {background: #e8445a;}
.ride-item {background: white; border: 1px solid #e4e4e7; border-radius: 16px; padding: 1.5rem;
            margin-bottom: 1rem;}
.success {color: #059669; background: #ecfdf5; padding: 1rem; border-radius: 12px; margin-bottom: 1rem;}
.error {color: #e8445a; background: #fef2f4; padding: 1rem; border-radius: 12px; margin-bottom: 1rem;}
#map {width: 100%; height: 400px; border-radius: 16px; margin: 1rem 0;}
h2 {font-size: 2rem; margin-bottom: 1.5rem; margin-top: 1rem;}
h3 {font-size: 1.25rem; margin-bottom: 1rem;}
p {line-height: 1.75; color: #52525b;}
</style>
</head>
<body>

<nav>
  <div class="logo">
    <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <g stroke="currentColor" stroke-width="8" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path d="M 20 50 Q 30 50 30 65 L 30 75"/><circle cx="50" cy="20" r="8"/><path d="M 50 28 L 50 75"/>
        <circle cx="50" cy="85" r="10"/><path d="M 50 75 L 65 85 L 65 70 L 50 75"/><path d="M 80 50 Q 90 50 90 65 L 90 75"/>
        <line x1="55" y1="55" x2="85" y2="55" stroke-width="6"/>
      </g>
    </svg>
    <span>RideLoop</span>
  </div>
  <div class="nav-links">
    <button onclick="showPage('home')">Home</button>
    <button onclick="showPage('search')">Find Ride</button>
    <button onclick="showPage('create')">Create</button>
    <button onclick="showPage('bookings')">Bookings</button>
    <button onclick="showPage('profile')">Profile</button>
  </div>
  <button class="nav-cta" id="authBtn">Sign In</button>
</nav>

<div class="modal" id="loginModal">
  <div class="modal-content">
    <h2>Sign In</h2>
    <div id="loginMsg"></div>
    <div class="form-group">
      <label class="form-label">Phone</label>
      <input type="tel" class="form-input" id="loginPhone" placeholder="+91 98765 43210">
    </div>
    <div class="form-group">
      <label class="form-label">Password</label>
      <input type="password" class="form-input" id="loginPassword">
    </div>
    <button class="btn" onclick="handleLogin()">Sign In</button>
    <p style="text-align: center; margin-top: 1rem;">No account? <a href="javascript:" onclick="closeModal('loginModal'); showModal('signupModal')" style="color: #e8445a;">Sign Up</a></p>
  </div>
</div>

<div class="modal" id="signupModal">
  <div class="modal-content">
    <h2>Create Account</h2>
    <div id="signupMsg"></div>
    <div class="form-group">
      <label class="form-label">Name</label>
      <input type="text" class="form-input" id="signupName">
    </div>
    <div class="form-group">
      <label class="form-label">Phone</label>
      <input type="tel" class="form-input" id="signupPhone" placeholder="+91 98765 43210">
    </div>
    <div class="form-group">
      <label class="form-label">Email</label>
      <input type="email" class="form-input" id="signupEmail">
    </div>
    <div class="form-group">
      <label class="form-label">Password</label>
      <input type="password" class="form-input" id="signupPassword">
    </div>
    <div class="form-group">
      <label class="form-label">I want to be a:</label>
      <select class="form-input" id="signupType">
        <option>Passenger</option>
        <option>Driver</option>
      </select>
    </div>
    <button class="btn" onclick="handleSignup()">Create Account</button>
  </div>
</div>

<div class="page on" id="homePage">
  <div class="container">
    <h1 style="font-size: 2.5rem; margin: 3rem 0 1rem;">Welcome to <span style="color: #e8445a;">RideLoop</span></h1>
    <p style="font-size: 1.05rem; margin-bottom: 2rem;">Smart ride-sharing with real-time location tracking and live Google Maps integration.</p>
    <button class="btn" onclick="showModal('loginModal')" style="margin-bottom: 1rem;">Get Started</button>
    <div style="background: white; border: 1px solid #e4e4e7; border-radius: 16px; padding: 2rem;">
      <h3>Features</h3>
      <ul style="margin: 1rem 0; padding-left: 1.5rem;">
        <li style="margin: 0.5rem 0;">✓ Real-time location with Google Maps</li>
        <li style="margin: 0.5rem 0;">✓ Search and book rides instantly</li>
        <li style="margin: 0.5rem 0;">✓ Create rides as a driver</li>
        <li style="margin: 0.5rem 0;">✓ Live location sharing</li>
        <li style="margin: 0.5rem 0;">✓ Editable driver profiles</li>
        <li style="margin: 0.5rem 0;">✓ Secure payments</li>
      </ul>
    </div>
  </div>
</div>

<div class="page" id="searchPage">
  <div class="container">
    <h2>Find a Ride</h2>
    <div style="background: white; border: 1px solid #e4e4e7; border-radius: 16px; padding: 1.5rem; margin-bottom: 2rem;">
      <div id="searchMsg"></div>
      <div class="form-group">
        <label class="form-label">From</label>
        <input type="text" class="form-input" id="searchFrom" placeholder="Delhi">
      </div>
      <div class="form-group">
        <label class="form-label">To</label>
        <input type="text" class="form-input" id="searchTo" placeholder="Mumbai">
      </div>
      <div class="form-group">
        <label class="form-label">Passengers</label>
        <input type="number" class="form-input" id="searchPassengers" value="1" min="1" max="6">
      </div>
      <button class="btn" onclick="handleSearch()">Search Rides</button>
    </div>
    <div id="searchResults"></div>
  </div>
</div>

<div class="page" id="createPage">
  <div class="container">
    <h2>Create a Ride</h2>
    <div style="background: white; border: 1px solid #e4e4e7; border-radius: 16px; padding: 1.5rem;">
      <div id="createMsg"></div>
      <div class="form-group">
        <label class="form-label">From Location</label>
        <input type="text" class="form-input" id="createFrom" placeholder="Pickup">
      </div>
      <div class="form-group">
        <label class="form-label">Coordinates (Lat, Lng)</label>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
          <input type="number" class="form-input" id="createFromLat" placeholder="Lat" step="0.0001">
          <input type="number" class="form-input" id="createFromLng" placeholder="Lng" step="0.0001">
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">To Location</label>
        <input type="text" class="form-input" id="createTo" placeholder="Dropoff">
      </div>
      <div class="form-group">
        <label class="form-label">Coordinates (Lat, Lng)</label>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
          <input type="number" class="form-input" id="createToLat" placeholder="Lat" step="0.0001">
          <input type="number" class="form-input" id="createToLng" placeholder="Lng" step="0.0001">
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">Departure Time</label>
        <input type="datetime-local" class="form-input" id="createTime">
      </div>
      <div class="form-group">
        <label class="form-label">Available Seats</label>
        <input type="number" class="form-input" id="createSeats" value="4" min="1" max="8">
      </div>
      <div class="form-group">
        <label class="form-label">Price per Seat (₹)</label>
        <input type="number" class="form-input" id="createPrice" placeholder="500" min="0">
      </div>
      <button class="btn" onclick="handleCreateRide()">Create Ride</button>
    </div>
  </div>
</div>

<div class="page" id="bookingsPage">
  <div class="container">
    <h2>My Bookings</h2>
    <div id="bookingsList"></div>
  </div>
</div>

<div class="page" id="profilePage">
  <div class="container">
    <h2>Profile</h2>
    <div id="profileContent"></div>
  </div>
</div>

<script>
const API_URL = 'http://localhost:5000/api';
let currentUser = null;
let map = null;

function showPage(page) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('on'));
  document.getElementById(page + 'Page').classList.add('on');
  if (page === 'bookings') loadBookings();
  if (page === 'profile') loadProfile();
}

function showModal(m) { document.getElementById(m).classList.add('on'); }
function closeModal(m) { document.getElementById(m).classList.remove('on'); }

async function handleLogin() {
  const phone = document.getElementById('loginPhone').value;
  const password = document.getElementById('loginPassword').value;
  if (!phone || !password) { document.getElementById('loginMsg').innerHTML = '<div class="error">Fill all fields</div>'; return; }
  try {
    const res = await fetch(`${API_URL}/auth/login`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, password })
    });
    const data = await res.json();
    if (res.ok) {
      currentUser = data.user;
      localStorage.setItem('token', data.token);
      closeModal('loginModal');
      updateUI();
      showPage('search');
      alert('Logged in!');
    } else { document.getElementById('loginMsg').innerHTML = `<div class="error">${data.error}</div>`; }
  } catch (e) { document.getElementById('loginMsg').innerHTML = `<div class="error">Error: ${e.message}</div>`; }
}

async function handleSignup() {
  const name = document.getElementById('signupName').value;
  const phone = document.getElementById('signupPhone').value;
  const email = document.getElementById('signupEmail').value;
  const password = document.getElementById('signupPassword').value;
  const type = document.getElementById('signupType').value.toLowerCase();
  if (!name || !phone || !email || !password) { document.getElementById('signupMsg').innerHTML = '<div class="error">Fill all fields</div>'; return; }
  try {
    const res = await fetch(`${API_URL}/auth/signup`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, phone, email, password, user_type: type })
    });
    const data = await res.json();
    if (res.ok) {
      currentUser = data.user;
      localStorage.setItem('token', data.token);
      closeModal('signupModal');
      updateUI();
      showPage('search');
      alert('Account created!');
    } else { document.getElementById('signupMsg').innerHTML = `<div class="error">${data.error}</div>`; }
  } catch (e) { document.getElementById('signupMsg').innerHTML = `<div class="error">Error: ${e.message}</div>`; }
}

async function handleSearch() {
  if (!currentUser) { alert('Login first'); showModal('loginModal'); return; }
  const from = document.getElementById('searchFrom').value;
  const to = document.getElementById('searchTo').value;
  const passengers = document.getElementById('searchPassengers').value;
  if (!from || !to) { document.getElementById('searchMsg').innerHTML = '<div class="error">Enter locations</div>'; return; }
  try {
    const res = await fetch(`${API_URL}/rides/search`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ from_location: from, to_location: to, passengers: parseInt(passengers) })
    });
    const data = await res.json();
    if (res.ok) {
      let html = '';
      if (data.rides.length > 0) {
        data.rides.forEach(ride => {
          const available = ride.available_seats - ride.booked_seats;
          html += `<div class="ride-item"><h4>${ride.driver_name}</h4><p><strong>${ride.from_location}</strong> → <strong>${ride.to_location}</strong></p>
            <p>Time: ${ride.departure_time}</p><p>Seats: ${available} | <strong style="color: #e8445a;">₹${ride.price_per_seat}/seat</strong></p>
            <button class="btn" onclick="bookRide(${ride.id})" style="margin-top: 1rem;">Book Ride</button></div>`;
        });
      } else { html = '<p>No rides found</p>'; }
      document.getElementById('searchResults').innerHTML = html;
    }
  } catch (e) { document.getElementById('searchMsg').innerHTML = `<div class="error">Error: ${e.message}</div>`; }
}

async function handleCreateRide() {
  if (!currentUser || currentUser.user_type !== 'driver') { alert('Drivers only'); return; }
  const from = document.getElementById('createFrom').value;
  const fLat = document.getElementById('createFromLat').value;
  const fLng = document.getElementById('createFromLng').value;
  const to = document.getElementById('createTo').value;
  const tLat = document.getElementById('createToLat').value;
  const tLng = document.getElementById('createToLng').value;
  const time = document.getElementById('createTime').value;
  const seats = document.getElementById('createSeats').value;
  const price = document.getElementById('createPrice').value;
  if (!from || !to || !time || !seats || !price || !fLat || !fLng || !tLat || !tLng) {
    document.getElementById('createMsg').innerHTML = '<div class="error">Fill all fields</div>'; return;
  }
  try {
    const res = await fetch(`${API_URL}/rides/create`, {
      method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ from_location: from, from_lat: parseFloat(fLat), from_lng: parseFloat(fLng),
        to_location: to, to_lat: parseFloat(tLat), to_lng: parseFloat(tLng), departure_time: time,
        available_seats: parseInt(seats), price_per_seat: parseFloat(price) })
    });
    const data = await res.json();
    if (res.ok) { document.getElementById('createMsg').innerHTML = '<div class="success">Ride created!</div>'; setTimeout(() => showPage('search'), 1000); }
    else { document.getElementById('createMsg').innerHTML = `<div class="error">${data.error}</div>`; }
  } catch (e) { document.getElementById('createMsg').innerHTML = `<div class="error">Error: ${e.message}</div>`; }
}

async function bookRide(rideId) {
  if (!currentUser) { alert('Login first'); showModal('loginModal'); return; }
  const passengers = prompt('Passengers:', '1');
  if (!passengers) return;
  try {
    const res = await fetch(`${API_URL}/bookings/create`, {
      method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ ride_id: rideId, num_passengers: parseInt(passengers) })
    });
    const data = await res.json();
    if (res.ok) { alert(`Booked! Total: ₹${Math.round(data.total)}`); loadBookings(); }
    else { alert(data.error); }
  } catch (e) { alert(`Error: ${e.message}`); }
}

async function loadBookings() {
  if (!currentUser) return;
  try {
    const res = await fetch(`${API_URL}/bookings`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } });
    const data = await res.json();
    let html = '';
    if (data.bookings && data.bookings.length > 0) {
      data.bookings.forEach(b => {
        html += `<div class="ride-item"><h4>${b.driver_name}</h4><p><strong>${b.from_location}</strong> → <strong>${b.to_location}</strong></p>
          <p>Time: ${b.departure_time}</p><p>Passengers: ${b.num_passengers} | Total: ₹${Math.round(b.total_amount)}</p></div>`;
      });
    } else { html = '<p>No bookings</p>'; }
    document.getElementById('bookingsList').innerHTML = html;
  } catch (e) { console.error(e); }
}

async function loadProfile() {
  if (!currentUser) { document.getElementById('profileContent').innerHTML = '<p>Login to see profile</p>'; return; }
  try {
    const res = await fetch(`${API_URL}/user/profile`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } });
    const user = await res.json();
    let html = `<div style="background: #eff6ff; border: 1px solid #2563eb; border-radius: 12px; padding: 1rem; margin-bottom: 1.5rem;">
      <h3>${user.name}</h3><p>Phone: ${user.phone}</p><p>Type: ${user.user_type} | Rating: ⭐ ${user.rating}</p></div>`;
    if (user.user_type === 'driver') {
      html += `<div style="background: white; border: 1px solid #e4e4e7; border-radius: 16px; padding: 1.5rem; margin-bottom: 2rem;">
        <h3>Edit Driver Profile</h3>
        <div class="form-group"><label class="form-label">Vehicle Name</label>
          <input type="text" class="form-input" id="vehicleName" value="${user.vehicle_name || ''}"></div>
        <div class="form-group"><label class="form-label">Vehicle Type</label>
          <input type="text" class="form-input" id="vehicleType" value="${user.vehicle_type || ''}"></div>
        <div class="form-group"><label class="form-label">License Plate</label>
          <input type="text" class="form-input" id="vehiclePlate" value="${user.vehicle_plate || ''}"></div>
        <button class="btn" onclick="updateProfile()">Save Profile</button></div>`;
    }
    html += `<div style="background: white; border: 1px solid #e4e4e7; border-radius: 16px; padding: 1.5rem; margin-bottom: 2rem;">
      <h3>Live Location</h3><button class="btn" onclick="shareLocation()">📍 Share My Location</button>
      <div id="map"></div></div>
      <button class="btn" onclick="handleLogout()" style="background: #e8445a;">Logout</button>`;
    document.getElementById('profileContent').innerHTML = html;
    setTimeout(() => initMap(), 500);
  } catch (e) { console.error(e); }
}

function initMap() {
  const mapDiv = document.getElementById('map');
  if (!mapDiv || mapDiv.offsetHeight === 0) return;
  map = new google.maps.Map(mapDiv, { zoom: 15, center: { lat: 28.6139, lng: 77.2090 } });
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition((pos) => {
      const lat = pos.coords.latitude, lng = pos.coords.longitude;
      map.setCenter({ lat, lng });
      new google.maps.Marker({ position: { lat, lng }, map: map, title: 'Your Location' });
    });
  }
}

async function shareLocation() {
  if (!currentUser) return;
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(async (pos) => {
      const lat = pos.coords.latitude, lng = pos.coords.longitude;
      try {
        await fetch(`${API_URL}/user/location`, {
          method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },
          body: JSON.stringify({ latitude: lat, longitude: lng })
        });
        alert('Location shared!');
        initMap();
      } catch (e) { alert(`Error: ${e.message}`); }
    });
  }
}

async function updateProfile() {
  const name = document.getElementById('vehicleName').value;
  const type = document.getElementById('vehicleType').value;
  const plate = document.getElementById('vehiclePlate').value;
  try {
    const res = await fetch(`${API_URL}/user/profile`, {
      method: 'PUT', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ vehicle_name: name, vehicle_type: type, vehicle_plate: plate })
    });
    if (res.ok) { alert('Profile updated!'); } else { alert('Error'); }
  } catch (e) { alert(`Error: ${e.message}`); }
}

function handleLogout() { currentUser = null; localStorage.removeItem('token'); updateUI(); showPage('home'); alert('Logged out'); }

function updateUI() {
  const btn = document.getElementById('authBtn');
  if (currentUser) { btn.textContent = `${currentUser.name} (Logout)`; btn.onclick = () => { if (confirm('Logout?')) handleLogout(); }; }
  else { btn.textContent = 'Sign In'; btn.onclick = () => showModal('loginModal'); }
}

window.addEventListener('load', () => {
  updateUI();
  document.getElementById('createTime').value = new Date().toISOString().slice(0, 16);
});
</script>

</body>
</html>'''

@app.route('/')
def serve():
    return FRONTEND_HTML

if __name__ == '__main__':
    init_db()
    insert_sample_data()
    app.run(debug=True, host='0.0.0.0', port=5000)
