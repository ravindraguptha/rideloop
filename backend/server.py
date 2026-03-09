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
            "phone": user["phone"],
            "gender": user.get("gender"),
            "role": user.get("role", "Passenger"),
            "women_only_preference": user.get("women_only_preference", False),
            "kyc_verified": user.get("kyc_verified", False)
        }
    }

@app.get("/api/auth/profile")
async def get_profile(token: str):
    user = await get_current_user(token)
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "phone": user["phone"],
        "gender": user.get("gender"),
        "role": user.get("role", "Passenger"),
        "women_only_preference": user.get("women_only_preference", False),
        "kyc_verified": user.get("kyc_verified", False)
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

# NEW ENDPOINTS FOR PROFILE FEATURES

@app.put("/api/auth/profile")
async def update_profile(profile: ProfileUpdate, token: str):
    user = await get_current_user(token)
    
    update_data = {}
    if profile.name is not None:
        update_data["name"] = profile.name
    if profile.gender is not None:
        update_data["gender"] = profile.gender
    if profile.role is not None:
        update_data["role"] = profile.role
    if profile.women_only_preference is not None:
        update_data["women_only_preference"] = profile.women_only_preference
    
    if update_data:
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": update_data}
        )
    
    updated_user = await db.users.find_one({"_id": user["_id"]})
    return {
        "id": str(updated_user["_id"]),
        "name": updated_user["name"],
        "phone": updated_user["phone"],
        "gender": updated_user.get("gender"),
        "role": updated_user.get("role", "Passenger"),
        "women_only_preference": updated_user.get("women_only_preference", False),
        "kyc_verified": updated_user.get("kyc_verified", False)
    }

@app.post("/api/kyc/verify")
async def verify_kyc(token: str):
    user = await get_current_user(token)
    
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"kyc_verified": True}}
    )
    
    return {"message": "KYC verified successfully", "kyc_verified": True}

@app.post("/api/vehicles")
async def add_vehicle(vehicle: VehicleCreate, token: str):
    user = await get_current_user(token)
    
    vehicle_doc = {
        "user_id": str(user["_id"]),
        "vehicle_type": vehicle.vehicle_type,
        "vehicle_number": vehicle.vehicle_number,
        "vehicle_model": vehicle.vehicle_model,
        "vehicle_color": vehicle.vehicle_color,
        "accept_requests": True,
        "created_at": datetime.utcnow()
    }
    result = await db.vehicles.insert_one(vehicle_doc)
    
    return {
        "id": str(result.inserted_id),
        "message": "Vehicle added successfully"
    }

@app.get("/api/vehicles")
async def get_vehicles(token: str):
    user = await get_current_user(token)
    
    vehicles = await db.vehicles.find({"user_id": str(user["_id"])}).to_list(100)
    result = []
    for vehicle in vehicles:
        result.append({
            "id": str(vehicle["_id"]),
            "vehicle_type": vehicle["vehicle_type"],
            "vehicle_number": vehicle["vehicle_number"],
            "vehicle_model": vehicle["vehicle_model"],
            "vehicle_color": vehicle["vehicle_color"],
            "accept_requests": vehicle.get("accept_requests", True)
        })
    
    return result

@app.put("/api/vehicles/{vehicle_id}")
async def update_vehicle(vehicle_id: str, vehicle: VehicleUpdate, token: str):
    user = await get_current_user(token)
    
    # Check if vehicle belongs to user
    existing = await db.vehicles.find_one({"_id": ObjectId(vehicle_id), "user_id": str(user["_id"])})
    if not existing:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    update_data = {}
    if vehicle.vehicle_type is not None:
        update_data["vehicle_type"] = vehicle.vehicle_type
    if vehicle.vehicle_number is not None:
        update_data["vehicle_number"] = vehicle.vehicle_number
    if vehicle.vehicle_model is not None:
        update_data["vehicle_model"] = vehicle.vehicle_model
    if vehicle.vehicle_color is not None:
        update_data["vehicle_color"] = vehicle.vehicle_color
    if vehicle.accept_requests is not None:
        update_data["accept_requests"] = vehicle.accept_requests
    
    if update_data:
        await db.vehicles.update_one(
            {"_id": ObjectId(vehicle_id)},
            {"$set": update_data}
        )
    
    return {"message": "Vehicle updated successfully"}

@app.delete("/api/vehicles/{vehicle_id}")
async def delete_vehicle(vehicle_id: str, token: str):
    user = await get_current_user(token)
    
    result = await db.vehicles.delete_one({"_id": ObjectId(vehicle_id), "user_id": str(user["_id"])})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    return {"message": "Vehicle deleted successfully"}

@app.get("/api/ride-requests")
async def get_ride_requests(token: str):
    user = await get_current_user(token)
    user_id = str(user["_id"])
    
    # Get rides created by this user
    rides = await db.rides.find({"creator_id": user_id}).to_list(100)
    ride_ids = [str(ride["_id"]) for ride in rides]
    
    # Get pending requests for these rides
    requests = await db.bookings.find({
        "ride_id": {"$in": ride_ids},
        "status": "pending"
    }).to_list(100)
    
    result = []
    for req in requests:
        ride = await db.rides.find_one({"_id": ObjectId(req["ride_id"])})
        if ride:
            result.append({
                "id": str(req["_id"]),
                "ride_id": req["ride_id"],
                "user_name": req["user_name"],
                "user_phone": req["user_phone"],
                "seats_requested": req["seats_booked"],
                "ride_route": f"{ride['start_location']} → {ride['destination']}",
                "ride_date": ride["date"],
                "ride_time": ride["time"],
                "status": req["status"]
            })
    
    return result

@app.put("/api/rides/{ride_id}/accept/{booking_id}")
async def accept_ride_request(ride_id: str, booking_id: str, token: str):
    user = await get_current_user(token)
    
    # Check if user is the ride creator
    ride = await db.rides.find_one({"_id": ObjectId(ride_id)})
    if not ride or ride["creator_id"] != str(user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get booking
    booking = await db.bookings.find_one({"_id": ObjectId(booking_id)})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check available seats
    if ride["available_seats"] < booking["seats_booked"]:
        raise HTTPException(status_code=400, detail="Not enough seats available")
    
    # Update booking status
    await db.bookings.update_one(
        {"_id": ObjectId(booking_id)},
        {"$set": {"status": "accepted"}}
    )
    
    # Update ride seats
    await db.rides.update_one(
        {"_id": ObjectId(ride_id)},
        {"$inc": {"available_seats": -booking["seats_booked"]}}
    )
    
    return {"message": "Ride request accepted"}

@app.put("/api/rides/{ride_id}/decline/{booking_id}")
async def decline_ride_request(ride_id: str, booking_id: str, token: str):
    user = await get_current_user(token)
    
    # Check if user is the ride creator
    ride = await db.rides.find_one({"_id": ObjectId(ride_id)})
    if not ride or ride["creator_id"] != str(user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Update booking status
    result = await db.bookings.update_one(
        {"_id": ObjectId(booking_id)},
        {"$set": {"status": "declined"}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    return {"message": "Ride request declined"}

@app.get("/api/earnings")
async def get_earnings(token: str):
    user = await get_current_user(token)
    user_id = str(user["_id"])
    
    # Get all rides created by user
    rides = await db.rides.find({"creator_id": user_id}).to_list(1000)
    
    total_earnings = 0
    completed_trips = 0
    
    for ride in rides:
        # Get accepted bookings for this ride
        bookings = await db.bookings.find({
            "ride_id": str(ride["_id"]),
            "status": "accepted"
        }).to_list(100)
        
        for booking in bookings:
            earnings = booking["seats_booked"] * ride["price_per_seat"]
            total_earnings += earnings
            completed_trips += 1
    
    return {
        "total_earnings": total_earnings,
        "completed_trips": completed_trips,
        "rides_created": len(rides)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)