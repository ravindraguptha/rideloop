from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from passlib.context import CryptContext
import jwt
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client.rideloop

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"

# Helper functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        return None

# Models
class UserSignup(BaseModel):
    name: str
    phone: str
    password: str

class UserLogin(BaseModel):
    phone: str
    password: str

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    role: Optional[str] = None
    women_only_preference: Optional[bool] = None

class VehicleCreate(BaseModel):
    vehicle_type: str
    vehicle_number: str
    vehicle_model: str
    vehicle_color: str

class VehicleUpdate(BaseModel):
    vehicle_type: Optional[str] = None
    vehicle_number: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_color: Optional[str] = None
    accept_requests: Optional[bool] = None

class RideCreate(BaseModel):
    start_location: str
    destination: str
    date: str
    time: str
    available_seats: int
    price_per_seat: float

class JoinRide(BaseModel):
    seats: int = 1

# Auth dependency
async def get_current_user(token: str):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("user_id")
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Routes
@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.post("/api/auth/signup")
async def signup(user: UserSignup):
    # Check if user exists
    existing = await db.users.find_one({"phone": user.phone})
    if existing:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    # Create user
    user_doc = {
        "name": user.name,
        "phone": user.phone,
        "password_hash": hash_password(user.password),
        "gender": None,
        "role": "Passenger",
        "women_only_preference": False,
        "kyc_verified": False,
        "created_at": datetime.utcnow()
    }
    result = await db.users.insert_one(user_doc)
    
    # Create token
    token = create_access_token({"user_id": str(result.inserted_id)})
    
    return {
        "token": token,
        "user": {
            "id": str(result.inserted_id),
            "name": user.name,
            "phone": user.phone,
            "gender": None,
            "role": "Passenger",
            "women_only_preference": False,
            "kyc_verified": False
        }
    }

@app.post("/api/auth/login")
async def login(credentials: UserLogin):
    # Find user
    user = await db.users.find_one({"phone": credentials.phone})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token
    token = create_access_token({"user_id": str(user["_id"])})
    
    return {
        "token": token,
        "user": {
            "id": str(user["_id"]),
            "name": user["name"],
            "phone": user["phone"]
        }
    }

@app.get("/api/auth/profile")
async def get_profile(token: str):
    user = await get_current_user(token)
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "phone": user["phone"]
    }

@app.post("/api/rides")
async def create_ride(ride: RideCreate, token: str):
    user = await get_current_user(token)
    
    ride_doc = {
        "creator_id": str(user["_id"]),
        "creator_name": user["name"],
        "creator_phone": user["phone"],
        "start_location": ride.start_location,
        "destination": ride.destination,
        "date": ride.date,
        "time": ride.time,
        "available_seats": ride.available_seats,
        "total_seats": ride.available_seats,
        "price_per_seat": ride.price_per_seat,
        "status": "active",
        "created_at": datetime.utcnow()
    }
    result = await db.rides.insert_one(ride_doc)
    
    return {
        "id": str(result.inserted_id),
        "message": "Ride created successfully"
    }

@app.get("/api/rides")
async def get_rides(start_location: Optional[str] = None, destination: Optional[str] = None):
    query = {"status": "active", "available_seats": {"$gt": 0}}
    
    if start_location:
        query["start_location"] = start_location
    if destination:
        query["destination"] = destination
    
    rides = await db.rides.find(query).sort("created_at", -1).to_list(100)
    
    result = []
    for ride in rides:
        result.append({
            "id": str(ride["_id"]),
            "creator_id": ride["creator_id"],
            "creator_name": ride["creator_name"],
            "creator_phone": ride["creator_phone"],
            "start_location": ride["start_location"],
            "destination": ride["destination"],
            "date": ride["date"],
            "time": ride["time"],
            "available_seats": ride["available_seats"],
            "total_seats": ride["total_seats"],
            "price_per_seat": ride["price_per_seat"],
            "status": ride["status"]
        })
    
    return result

@app.post("/api/rides/{ride_id}/join")
async def join_ride(ride_id: str, join_data: JoinRide, token: str):
    user = await get_current_user(token)
    
    # Get ride
    ride = await db.rides.find_one({"_id": ObjectId(ride_id)})
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    
    # Check if user is creator
    if ride["creator_id"] == str(user["_id"]):
        raise HTTPException(status_code=400, detail="Cannot join your own ride")
    
    # Check if already joined
    existing_booking = await db.bookings.find_one({
        "ride_id": ride_id,
        "user_id": str(user["_id"]),
        "status": "confirmed"
    })
    if existing_booking:
        raise HTTPException(status_code=400, detail="Already joined this ride")
    
    # Check available seats
    if ride["available_seats"] < join_data.seats:
        raise HTTPException(status_code=400, detail="Not enough seats available")
    
    # Create booking
    booking_doc = {
        "ride_id": ride_id,
        "user_id": str(user["_id"]),
        "user_name": user["name"],
        "user_phone": user["phone"],
        "seats_booked": join_data.seats,
        "status": "confirmed",
        "created_at": datetime.utcnow()
    }
    await db.bookings.insert_one(booking_doc)
    
    # Update ride seats
    await db.rides.update_one(
        {"_id": ObjectId(ride_id)},
        {"$inc": {"available_seats": -join_data.seats}}
    )
    
    return {"message": "Successfully joined the ride"}

@app.get("/api/my-rides")
async def get_my_rides(token: str):
    user = await get_current_user(token)
    user_id = str(user["_id"])
    
    # Get created rides
    created_rides = await db.rides.find({"creator_id": user_id}).sort("created_at", -1).to_list(100)
    created = []
    for ride in created_rides:
        # Get bookings for this ride
        bookings = await db.bookings.find({"ride_id": str(ride["_id"]), "status": "confirmed"}).to_list(100)
        passengers = [{
            "name": b["user_name"],
            "phone": b["user_phone"],
            "seats": b["seats_booked"]
        } for b in bookings]
        
        created.append({
            "id": str(ride["_id"]),
            "start_location": ride["start_location"],
            "destination": ride["destination"],
            "date": ride["date"],
            "time": ride["time"],
            "available_seats": ride["available_seats"],
            "total_seats": ride["total_seats"],
            "price_per_seat": ride["price_per_seat"],
            "status": ride["status"],
            "passengers": passengers
        })
    
    # Get joined rides
    bookings = await db.bookings.find({"user_id": user_id, "status": "confirmed"}).to_list(100)
    joined = []
    for booking in bookings:
        ride = await db.rides.find_one({"_id": ObjectId(booking["ride_id"])})
        if ride:
            joined.append({
                "id": str(ride["_id"]),
                "creator_name": ride["creator_name"],
                "creator_phone": ride["creator_phone"],
                "start_location": ride["start_location"],
                "destination": ride["destination"],
                "date": ride["date"],
                "time": ride["time"],
                "seats_booked": booking["seats_booked"],
                "price_per_seat": ride["price_per_seat"],
                "status": ride["status"]
            })
    
    return {
        "created": created,
        "joined": joined
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)