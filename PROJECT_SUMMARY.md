# RideLoop - Ride Sharing Mobile App

## Overview
RideLoop is a lightweight ride-sharing mobile application built with Expo (React Native), FastAPI, and MongoDB. It allows users to create and join rides within Hyderabad.

## Tech Stack
- **Frontend**: Expo / React Native
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **State Management**: React Context API
- **Storage**: AsyncStorage

## Features Implemented

### 1. User Authentication ✅
- User signup with name, phone, and password
- User login with phone and password
- Secure password hashing using bcrypt
- JWT token-based authentication
- Persistent login sessions

### 2. Create Ride ✅
- Create rides with:
  - Start location (Hyderabad areas dropdown)
  - Destination (Hyderabad areas dropdown)
  - Date and time
  - Available seats (1-8)
  - Price per seat
- Validation for all fields
- Mobile-friendly form interface

### 3. Find Rides ✅
- Browse all available rides
- Filter by start location
- Filter by destination
- Filter by both locations
- Real-time availability display
- Pull-to-refresh functionality
- Join ride with one tap

### 4. Join Ride ✅
- Request seats in available rides
- Automatic seat count reduction
- Prevention of joining own rides
- Prevention of duplicate bookings
- Seat availability validation
- Driver contact information display

### 5. Dashboard ✅
- View created rides with passenger details
- View joined rides with driver details
- Two-tab interface (Created/Joined)
- Real-time ride status
- Passenger contact information for created rides
- Driver contact information for joined rides

### 6. Profile ✅
- Display user information
- Logout functionality
- About section

### 7. Hyderabad Locations
Complete list of 20 locations:
- Gachibowli, Hitech City, Madhapur, Kukatpally, Ameerpet
- Banjara Hills, Jubilee Hills, Begumpet, Secunderabad, Kondapur
- Miyapur, LB Nagar, Uppal, Dilsukhnagar, Charminar
- Mehdipatnam, Tarnaka, Koti, Somajiguda, Nagole

## Project Structure

```
/app
├── backend/
│   ├── server.py          # FastAPI backend with all endpoints
│   ├── requirements.txt   # Python dependencies
│   └── .env              # Backend environment variables
│
├── frontend/
│   ├── app/
│   │   ├── index.tsx                 # Auth screen (Login/Signup)
│   │   ├── _layout.tsx               # Root layout with auth provider
│   │   └── (tabs)/
│   │       ├── _layout.tsx           # Tab navigation layout
│   │       ├── home.tsx              # Find rides screen
│   │       ├── create.tsx            # Create ride screen
│   │       ├── dashboard.tsx         # My rides screen
│   │       └── profile.tsx           # Profile screen
│   │
│   ├── contexts/
│   │   └── AuthContext.tsx           # Authentication context
│   │
│   ├── app.json                      # Expo configuration
│   ├── package.json                  # Node dependencies
│   └── .env                          # Frontend environment variables
```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/login` - Login existing user
- `GET /api/auth/profile?token={token}` - Get user profile

### Rides
- `GET /api/rides` - Get all available rides (with optional filters)
- `GET /api/rides?start_location={location}` - Filter by start location
- `GET /api/rides?destination={location}` - Filter by destination
- `POST /api/rides?token={token}` - Create new ride
- `POST /api/rides/{ride_id}/join?token={token}` - Join a ride

### Dashboard
- `GET /api/my-rides?token={token}` - Get user's created and joined rides

### Health Check
- `GET /api/health` - API health status

## Database Schema

### Users Collection
```javascript
{
  _id: ObjectId,
  name: String,
  phone: String,  // Unique
  password_hash: String,
  created_at: DateTime
}
```

### Rides Collection
```javascript
{
  _id: ObjectId,
  creator_id: String,
  creator_name: String,
  creator_phone: String,
  start_location: String,
  destination: String,
  date: String,
  time: String,
  available_seats: Number,
  total_seats: Number,
  price_per_seat: Float,
  status: String,  // "active"
  created_at: DateTime
}
```

### Bookings Collection
```javascript
{
  _id: ObjectId,
  ride_id: String,
  user_id: String,
  user_name: String,
  user_phone: String,
  seats_booked: Number,
  status: String,  // "confirmed"
  created_at: DateTime
}
```

## App Preview

**Live URL**: https://rideloop-app.preview.emergentagent.com

The app features:
- Clean, minimal UI with green theme
- Mobile-responsive design
- Touch-friendly interface (48px minimum touch targets)
- Tab-based navigation
- Pull-to-refresh on list screens
- Loading states and error handling
- Mobile-optimized forms with proper keyboard handling

## Design Highlights

1. **Color Scheme**:
   - Primary: #4CAF50 (Green)
   - Background: #f5f5f5 (Light Gray)
   - Cards: #fff (White)
   - Text: #333 (Dark Gray)

2. **Typography**:
   - Clear hierarchy with font sizes (14px - 32px)
   - Bold headings for emphasis
   - Readable body text

3. **Mobile-First**:
   - 390x844 viewport (iPhone standard)
   - Thumb-friendly touch targets
   - Keyboard-aware scrolling
   - Native mobile components

4. **User Experience**:
   - Immediate feedback on actions
   - Clear error messages
   - Confirmation dialogs for important actions
   - Loading indicators during async operations

## Security Features

- Bcrypt password hashing
- JWT token authentication
- Token-based API authorization
- Input validation on backend
- Duplicate booking prevention
- Own-ride join prevention

## Testing Results

### Backend Testing ✅
All API endpoints tested and working:
- ✅ User signup and login
- ✅ Authentication error handling
- ✅ Ride creation with validation
- ✅ Ride search and filtering
- ✅ Join ride functionality
- ✅ Seat count management
- ✅ Dashboard data retrieval
- ✅ Proper HTTP status codes (200, 400, 401, 422)

### Frontend Testing ✅
- ✅ App loads successfully on web
- ✅ Authentication screen displays correctly
- ✅ Mobile-responsive design
- ✅ Clean UI with RideLoop branding

## How to Use

1. **Sign Up**: Create an account with name, phone, and password
2. **Create Ride**: Add ride details including locations, date, time, seats, and price
3. **Find Rides**: Browse available rides and filter by locations
4. **Join Ride**: Book seats in rides going to your destination
5. **Dashboard**: View your created rides with passenger details and joined rides with driver info
6. **Profile**: View your account information

## Future Enhancements (Not Implemented)

- Real-time chat between riders
- Payment gateway integration
- Google Maps integration
- Push notifications
- Ride ratings and reviews
- Real-time location tracking
- Ride history
- User verification badges
- In-app messaging
- Ride cancellation

## Notes

- Simple, lightweight implementation as requested
- No external integrations (maps, payments, chat)
- Focus on core ride-sharing functionality
- Optimized for mobile experience
- Production-ready backend with proper validations
