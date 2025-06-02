import os
import cv2
import face_recognition
import numpy as np
import datetime
import pygame
import hashlib
from pymongo import MongoClient
from gridfs import GridFS
from bson import Binary
from pygame.locals import *

class PlayerAuth:
    def __init__(self):
        """Initialize MongoDB connection and camera"""
        try:
            self.client = MongoClient('mongodb://localhost:27017/', 
                                    serverSelectionTimeoutMS=5000,
                                    connectTimeoutMS=10000,
                                    socketTimeoutMS=10000)
            self.client.server_info()  # Test connection
            self.db = self.client['alien_invasion_db']
            self.players = self.db.players
            self.fs = GridFS(self.db)
            
            # Create indexes if they don't exist
            self.players.create_index("username", unique=True)
            self.players.create_index("high_score")
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise
        
        # Camera initialization
        self.cap = None
        self.init_camera()
        
        # Initialize pygame mixer for sound feedback
        pygame.mixer.init()
        try:
            self.capture_sound = pygame.mixer.Sound('assets/camera_shutter.wav')
        except:
            self.capture_sound = None
            print("Warning: Could not load camera shutter sound")

    def _hash_password(self, password):
        """Simple SHA-256 password hashing with salt"""
        salt = "alien_invasion_salt"  # Should be unique per installation
        return hashlib.sha256((password + salt).encode()).hexdigest()

    def init_camera(self):
        """Initialize the camera with multiple fallback options"""
        if self.cap is None:
            # Try different camera indexes
            for i in range(3):  # Try up to 3 different camera indexes
                self.cap = cv2.VideoCapture(i)
                if self.cap.isOpened():
                    # Set camera resolution for better face recognition
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    break
                if self.cap:
                    self.cap.release()

    def register_player(self, username, password, photo):
        """Register new player with photo in MongoDB"""
        try:
            # Input validation
            if not username or not password or photo is None:
                print("Invalid input parameters")
                return False
                
            # Check if username exists
            if self.players.find_one({"username": username}):
                print("Username already exists")
                return False
                
            # Convert to RGB for face detection
            rgb_photo = cv2.cvtColor(photo, cv2.COLOR_BGR2RGB)
            
            # Face detection validation
            face_locations = face_recognition.face_locations(rgb_photo)
            if not face_locations:
                print("No face detected in photo")
                return False
                
            # Convert photo to binary
            _, buffer = cv2.imencode('.jpg', photo)
            photo_binary = Binary(buffer.tobytes())
            
            # Store in GridFS and get file ID
            photo_id = self.fs.put(photo_binary, filename=f"{username}_photo.jpg")
            
            # Create player document with hashed password
            player_data = {
                "username": username,
                "password": self._hash_password(password),
                "photo_id": photo_id,
                "high_score": 0,
                "created_at": datetime.datetime.now(),
                "last_login": datetime.datetime.now()
            }
            
            # Insert into database
            result = self.players.insert_one(player_data)
            
            # Play capture sound if available
            if self.capture_sound:
                self.capture_sound.play()
                
            print(f"Registered new player: {username}")
            return True
            
        except Exception as e:
            print(f"Registration error: {e}")
            return False

    def verify_player(self, username, password, camera_photo):
        """Verify player credentials and face against MongoDB"""
        try:
            # Input validation
            if not username or not password or camera_photo is None:
                return False
                
            # Find player in database
            player = self.players.find_one({"username": username})
            if not player:
                print("Player not found")
                return False
                
            # Verify password
            if player["password"] != self._hash_password(password):
                print("Password mismatch")
                return False
                
            # Get stored photo from GridFS
            stored_photo = self.fs.get(player["photo_id"]).read()
            nparr = np.frombuffer(stored_photo, np.uint8)
            stored_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Convert both images to RGB
            rgb_stored = cv2.cvtColor(stored_image, cv2.COLOR_BGR2RGB)
            rgb_camera = cv2.cvtColor(camera_photo, cv2.COLOR_BGR2RGB)
            
            # Get face encodings
            stored_encoding = face_recognition.face_encodings(rgb_stored)
            camera_encoding = face_recognition.face_encodings(rgb_camera)
            
            if not stored_encoding or not camera_encoding:
                print("Could not extract face encodings")
                return False
                
            # Compare faces
            matches = face_recognition.compare_faces([stored_encoding[0]], camera_encoding[0])
            
            # Update last login time if successful
            if matches[0]:
                self.players.update_one(
                    {"username": username},
                    {"$set": {"last_login": datetime.datetime.now()}}
                )
                if self.capture_sound:
                    self.capture_sound.play()
                print("Login successful")
            
            return matches[0]
            
        except Exception as e:
            print(f"Verification error: {e}")
            return False

    def capture_photo(self):
        """Capture photo from webcam with retries and validation"""
        self.init_camera()
        if self.cap and self.cap.isOpened():
            for _ in range(3):  # Try 3 times to get a good frame
                ret, frame = self.cap.read()
                if ret:
                    # Verify the frame contains a face
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    face_locations = face_recognition.face_locations(rgb_frame)
                    if face_locations:
                        return frame
                    else:
                        print("No face detected in captured frame")
        else:
            print("Camera not available")
        return None
    
    def get_camera_frame(self, mirror=True):
        """Get a frame for preview with optional mirroring"""
        self.init_camera()
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                if mirror:
                    frame = cv2.flip(frame, 1)
                return frame
        return None
    
    def release_camera(self):
        """Release camera resources"""
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.cap = None

    def update_high_score(self, username, new_score):
        """Update player's high score in MongoDB"""
        try:
            result = self.players.update_one(
                {"username": username},
                {"$max": {"high_score": new_score}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating high score: {e}")
            return False

    def get_player_data(self, username):
        """Get all player data by username"""
        try:
            return self.players.find_one({"username": username}, {"_id": 0})
        except Exception as e:
            print(f"Error getting player data: {e}")
            return None

    def get_leaderboard(self, limit=10):
        """Get top players by high score with additional info"""
        try:
            return list(self.players.find(
                {},
                {"username": 1, "high_score": 1, "last_login": 1}
            ).sort("high_score", -1).limit(limit))
        except Exception as e:
            print(f"Error getting leaderboard: {e}")
            return []
    
    def __del__(self):
        """Cleanup resources when object is destroyed"""
        self.release_camera()
        if hasattr(self, 'client'):
            self.client.close()