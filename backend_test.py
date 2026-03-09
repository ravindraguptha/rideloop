#!/usr/bin/env python3
"""
RideLoop Backend API Testing Suite
Tests all backend endpoints for the ride-sharing application
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
BASE_URL = "https://rideloop-app.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class RideLoopTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS
        self.test_results = []
        self.user1_token = None
        self.user2_token = None
        self.test_ride_id = None
        self.timestamp = str(int(time.time()))
        self.user1_phone = f"987654{self.timestamp[-4:]}"
        self.user2_phone = f"876543{self.timestamp[-4:]}"
        
    def log_result(self, test_name, success, message, details=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {details}")
    
    def make_request(self, method, endpoint, data=None, params=None):
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data, params=params, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            return None, str(e)
    
    def test_health_check(self):
        """Test health endpoint"""
        print("\n=== Testing Health Check ===")
        response = self.make_request("GET", "/health")
        
        if response is None:
            self.log_result("Health Check", False, "Failed to connect to server")
            return False
            
        if response.status_code == 200:
            self.log_result("Health Check", True, "Server is healthy")
            return True
        else:
            self.log_result("Health Check", False, f"Health check failed with status {response.status_code}")
            return False
    
    def test_user_signup(self):
        """Test user registration"""
        print("\n=== Testing User Signup ===")
        
        # Test 1: Valid signup for user 1
        timestamp = str(int(time.time()))
        user1_data = {
            "name": "Sarah Johnson",
            "phone": f"987654{timestamp[-4:]}",
            "password": "securepass123"
        }
        
        response = self.make_request("POST", "/auth/signup", user1_data)
        if response is None:
            self.log_result("User1 Signup", False, "Failed to connect to signup endpoint")
            return False
            
        if response.status_code == 200:
            data = response.json()
            if "token" in data and "user" in data:
                self.user1_token = data["token"]
                self.log_result("User1 Signup", True, f"User {data['user']['name']} registered successfully")
            else:
                self.log_result("User1 Signup", False, "Missing token or user data in response", data)
                return False
        else:
            self.log_result("User1 Signup", False, f"Signup failed with status {response.status_code}", response.text)
            return False
        
        # Test 2: Valid signup for user 2
        user2_data = {
            "name": "Mike Chen",
            "phone": f"876543{timestamp[-4:]}",
            "password": "mypassword456"
        }
        
        response = self.make_request("POST", "/auth/signup", user2_data)
        if response and response.status_code == 200:
            data = response.json()
            if "token" in data:
                self.user2_token = data["token"]
                self.log_result("User2 Signup", True, f"User {data['user']['name']} registered successfully")
            else:
                self.log_result("User2 Signup", False, "Missing token in response", data)
        else:
            self.log_result("User2 Signup", False, f"User2 signup failed with status {response.status_code if response else 'No response'}")
        
        # Test 3: Duplicate signup (should fail)
        response = self.make_request("POST", "/auth/signup", user1_data)
        if response and response.status_code == 400:
            self.log_result("Duplicate Signup Prevention", True, "Correctly rejected duplicate phone number")
        else:
            self.log_result("Duplicate Signup Prevention", False, f"Should have rejected duplicate signup, got status {response.status_code if response else 'No response'}")
        
        return self.user1_token is not None and self.user2_token is not None
    
    def test_user_login(self):
        """Test user login"""
        print("\n=== Testing User Login ===")
        
        # Get timestamp for consistent phone numbers
        timestamp = str(int(time.time()))
        
        # Test 1: Valid login
        login_data = {
            "phone": f"987654{timestamp[-4:]}",
            "password": "securepass123"
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        if response and response.status_code == 200:
            data = response.json()
            if "token" in data and "user" in data:
                self.log_result("Valid Login", True, f"Login successful for {data['user']['name']}")
            else:
                self.log_result("Valid Login", False, "Missing token or user data", data)
        else:
            self.log_result("Valid Login", False, f"Login failed with status {response.status_code if response else 'No response'}")
        
        # Test 2: Invalid password
        invalid_login = {
            "phone": f"987654{timestamp[-4:]}",
            "password": "wrongpassword"
        }
        
        response = self.make_request("POST", "/auth/login", invalid_login)
        if response and response.status_code == 401:
            self.log_result("Invalid Password Login", True, "Correctly rejected invalid password")
        else:
            self.log_result("Invalid Password Login", False, f"Should have rejected invalid password, got status {response.status_code if response else 'No response'}")
        
        # Test 3: Non-existent user
        nonexistent_login = {
            "phone": "1111111111",
            "password": "anypassword"
        }
        
        response = self.make_request("POST", "/auth/login", nonexistent_login)
        if response and response.status_code == 401:
            self.log_result("Non-existent User Login", True, "Correctly rejected non-existent user")
        else:
            self.log_result("Non-existent User Login", False, f"Should have rejected non-existent user, got status {response.status_code if response else 'No response'}")
    
    def test_ride_creation(self):
        """Test ride creation"""
        print("\n=== Testing Ride Creation ===")
        
        if not self.user1_token:
            self.log_result("Ride Creation Setup", False, "No user token available for testing")
            return False
        
        # Test 1: Valid ride creation
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        ride_data = {
            "start_location": "Downtown Seattle",
            "destination": "Seattle Airport",
            "date": tomorrow,
            "time": "14:30",
            "available_seats": 3,
            "price_per_seat": 25.50
        }
        
        response = self.make_request("POST", "/rides", ride_data, params={"token": self.user1_token})
        if response and response.status_code == 200:
            data = response.json()
            if "id" in data:
                self.test_ride_id = data["id"]
                self.log_result("Valid Ride Creation", True, f"Ride created successfully with ID: {data['id']}")
            else:
                self.log_result("Valid Ride Creation", False, "Missing ride ID in response", data)
        else:
            self.log_result("Valid Ride Creation", False, f"Ride creation failed with status {response.status_code if response else 'No response'}")
        
        # Test 2: Ride creation without token (should fail)
        response = self.make_request("POST", "/rides", ride_data)
        if response and response.status_code == 401:
            self.log_result("Unauthorized Ride Creation", True, "Correctly rejected ride creation without token")
        else:
            self.log_result("Unauthorized Ride Creation", False, f"Should have rejected unauthorized request, got status {response.status_code if response else 'No response'}")
        
        return self.test_ride_id is not None
    
    def test_find_rides(self):
        """Test ride search and filtering"""
        print("\n=== Testing Find Rides ===")
        
        # Test 1: Get all rides
        response = self.make_request("GET", "/rides")
        if response and response.status_code == 200:
            rides = response.json()
            if isinstance(rides, list):
                self.log_result("Get All Rides", True, f"Retrieved {len(rides)} rides")
                
                # Verify our test ride is in the list
                if self.test_ride_id:
                    found_test_ride = any(ride["id"] == self.test_ride_id for ride in rides)
                    if found_test_ride:
                        self.log_result("Test Ride Visibility", True, "Created ride appears in rides list")
                    else:
                        self.log_result("Test Ride Visibility", False, "Created ride not found in rides list")
            else:
                self.log_result("Get All Rides", False, "Response is not a list", rides)
        else:
            self.log_result("Get All Rides", False, f"Failed to get rides, status {response.status_code if response else 'No response'}")
        
        # Test 2: Filter by start location
        response = self.make_request("GET", "/rides", params={"start_location": "Downtown Seattle"})
        if response and response.status_code == 200:
            rides = response.json()
            if isinstance(rides, list):
                matching_rides = [r for r in rides if r.get("start_location") == "Downtown Seattle"]
                if len(matching_rides) == len(rides):
                    self.log_result("Filter by Start Location", True, f"Found {len(rides)} rides from Downtown Seattle")
                else:
                    self.log_result("Filter by Start Location", False, f"Filter not working properly: {len(matching_rides)}/{len(rides)} rides match")
            else:
                self.log_result("Filter by Start Location", False, "Response is not a list")
        else:
            self.log_result("Filter by Start Location", False, f"Failed to filter rides, status {response.status_code if response else 'No response'}")
        
        # Test 3: Filter by destination
        response = self.make_request("GET", "/rides", params={"destination": "Seattle Airport"})
        if response and response.status_code == 200:
            rides = response.json()
            if isinstance(rides, list):
                matching_rides = [r for r in rides if r.get("destination") == "Seattle Airport"]
                if len(matching_rides) == len(rides):
                    self.log_result("Filter by Destination", True, f"Found {len(rides)} rides to Seattle Airport")
                else:
                    self.log_result("Filter by Destination", False, f"Filter not working properly: {len(matching_rides)}/{len(rides)} rides match")
            else:
                self.log_result("Filter by Destination", False, "Response is not a list")
        else:
            self.log_result("Filter by Destination", False, f"Failed to filter rides, status {response.status_code if response else 'No response'}")
        
        # Test 4: Filter by both start and destination
        response = self.make_request("GET", "/rides", params={
            "start_location": "Downtown Seattle",
            "destination": "Seattle Airport"
        })
        if response and response.status_code == 200:
            rides = response.json()
            if isinstance(rides, list):
                self.log_result("Filter by Both Locations", True, f"Found {len(rides)} rides matching both criteria")
            else:
                self.log_result("Filter by Both Locations", False, "Response is not a list")
        else:
            self.log_result("Filter by Both Locations", False, f"Failed to filter rides, status {response.status_code if response else 'No response'}")
    
    def test_join_ride(self):
        """Test joining rides"""
        print("\n=== Testing Join Ride ===")
        
        if not self.test_ride_id or not self.user2_token:
            self.log_result("Join Ride Setup", False, "Missing test ride ID or user2 token")
            return False
        
        # Test 1: Valid join ride
        join_data = {"seats": 1}
        response = self.make_request("POST", f"/rides/{self.test_ride_id}/join", join_data, params={"token": self.user2_token})
        if response and response.status_code == 200:
            self.log_result("Valid Join Ride", True, "Successfully joined ride")
        else:
            self.log_result("Valid Join Ride", False, f"Failed to join ride, status {response.status_code if response else 'No response'}")
        
        # Test 2: Join own ride (should fail)
        response = self.make_request("POST", f"/rides/{self.test_ride_id}/join", join_data, params={"token": self.user1_token})
        if response and response.status_code == 400:
            self.log_result("Join Own Ride Prevention", True, "Correctly prevented joining own ride")
        else:
            self.log_result("Join Own Ride Prevention", False, f"Should have prevented joining own ride, got status {response.status_code if response else 'No response'}")
        
        # Test 3: Join same ride twice (should fail)
        response = self.make_request("POST", f"/rides/{self.test_ride_id}/join", join_data, params={"token": self.user2_token})
        if response and response.status_code == 400:
            self.log_result("Duplicate Join Prevention", True, "Correctly prevented duplicate join")
        else:
            self.log_result("Duplicate Join Prevention", False, f"Should have prevented duplicate join, got status {response.status_code if response else 'No response'}")
        
        # Test 4: Verify seat count decreased
        response = self.make_request("GET", "/rides")
        if response and response.status_code == 200:
            rides = response.json()
            test_ride = next((r for r in rides if r["id"] == self.test_ride_id), None)
            if test_ride:
                if test_ride["available_seats"] == 2:  # Should be 3-1=2
                    self.log_result("Seat Count Update", True, f"Available seats correctly updated to {test_ride['available_seats']}")
                else:
                    self.log_result("Seat Count Update", False, f"Expected 2 available seats, got {test_ride['available_seats']}")
            else:
                self.log_result("Seat Count Update", False, "Could not find test ride to verify seat count")
        
        # Test 5: Join without token (should fail)
        response = self.make_request("POST", f"/rides/{self.test_ride_id}/join", join_data)
        if response and response.status_code == 401:
            self.log_result("Unauthorized Join Prevention", True, "Correctly prevented unauthorized join")
        else:
            self.log_result("Unauthorized Join Prevention", False, f"Should have prevented unauthorized join, got status {response.status_code if response else 'No response'}")
        
        # Test 6: Try to join with more seats than available
        many_seats_data = {"seats": 5}  # More than the 2 remaining seats
        response = self.make_request("POST", f"/rides/{self.test_ride_id}/join", many_seats_data, params={"token": self.user2_token})
        if response and response.status_code == 400:
            self.log_result("Insufficient Seats Prevention", True, "Correctly prevented joining when not enough seats")
        else:
            self.log_result("Insufficient Seats Prevention", False, f"Should have prevented joining with insufficient seats, got status {response.status_code if response else 'No response'}")
    
    def test_dashboard(self):
        """Test user dashboard (my rides)"""
        print("\n=== Testing Dashboard ===")
        
        if not self.user1_token or not self.user2_token:
            self.log_result("Dashboard Setup", False, "Missing user tokens")
            return False
        
        # Test 1: Get created rides for user1
        response = self.make_request("GET", "/my-rides", params={"token": self.user1_token})
        if response and response.status_code == 200:
            data = response.json()
            if "created" in data and "joined" in data:
                created_rides = data["created"]
                if isinstance(created_rides, list) and len(created_rides) > 0:
                    self.log_result("User1 Created Rides", True, f"Found {len(created_rides)} created rides")
                    
                    # Check if passenger list is included
                    test_ride = next((r for r in created_rides if r["id"] == self.test_ride_id), None)
                    if test_ride and "passengers" in test_ride:
                        passengers = test_ride["passengers"]
                        if len(passengers) == 1:
                            self.log_result("Passenger List", True, f"Found {len(passengers)} passenger in created ride")
                        else:
                            self.log_result("Passenger List", False, f"Expected 1 passenger, found {len(passengers)}")
                    else:
                        self.log_result("Passenger List", False, "Passenger list not found in created ride")
                else:
                    self.log_result("User1 Created Rides", False, "No created rides found or invalid format")
            else:
                self.log_result("User1 Created Rides", False, "Missing 'created' or 'joined' in response", data)
        else:
            self.log_result("User1 Created Rides", False, f"Failed to get dashboard, status {response.status_code if response else 'No response'}")
        
        # Test 2: Get joined rides for user2
        response = self.make_request("GET", "/my-rides", params={"token": self.user2_token})
        if response and response.status_code == 200:
            data = response.json()
            if "joined" in data:
                joined_rides = data["joined"]
                if isinstance(joined_rides, list) and len(joined_rides) > 0:
                    self.log_result("User2 Joined Rides", True, f"Found {len(joined_rides)} joined rides")
                else:
                    self.log_result("User2 Joined Rides", False, "No joined rides found")
            else:
                self.log_result("User2 Joined Rides", False, "Missing 'joined' in response")
        else:
            self.log_result("User2 Joined Rides", False, f"Failed to get dashboard, status {response.status_code if response else 'No response'}")
        
        # Test 3: Dashboard without token (should fail)
        response = self.make_request("GET", "/my-rides")
        if response and response.status_code == 401:
            self.log_result("Unauthorized Dashboard Access", True, "Correctly prevented unauthorized dashboard access")
        else:
            self.log_result("Unauthorized Dashboard Access", False, f"Should have prevented unauthorized access, got status {response.status_code if response else 'No response'}")
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting RideLoop Backend API Tests")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        # Run tests in sequence
        if not self.test_health_check():
            print("❌ Health check failed - stopping tests")
            return False
        
        if not self.test_user_signup():
            print("❌ User signup failed - stopping tests")
            return False
        
        self.test_user_login()
        
        if not self.test_ride_creation():
            print("❌ Ride creation failed - some tests may be skipped")
        
        self.test_find_rides()
        self.test_join_ride()
        self.test_dashboard()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        failed_tests = [result for result in self.test_results if not result["success"]]
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['message']}")
                if test['details']:
                    print(f"    Details: {test['details']}")
        
        print("\n✅ All tests completed!")
        return passed == total

if __name__ == "__main__":
    tester = RideLoopTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)