
import os
from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional, List
import bcrypt
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from bson.objectid import ObjectId
import shutil

# Load environment variables
load_dotenv()

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Create necessary directories
uploads_dir = Path("static/uploads")
uploads_dir.mkdir(parents=True, exist_ok=True)

templates_dir = Path("templates")
templates_dir.mkdir(parents=True, exist_ok=True)

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/enejistats")
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")

try:
    client = MongoClient(MONGO_URI)
    db = client.enejistats
    users_collection = db.users
    print("Connected to MongoDB successfully")
except Exception as e:
    print(f"MongoDB connection error: {e}")
    client = None
    db = None
    users_collection = None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request, error: Optional[str] = None, success: Optional[str] = None):
    return templates.TemplateResponse("register.html", {
        "request": request, 
        "error": error, 
        "success": success
    })

@app.post("/register")
async def register_user(
    request: Request,
    userType: str = Form(...),
    firstName: Optional[str] = Form(None),
    middleName: Optional[str] = Form(None),
    lastName: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    confirmPassword: Optional[str] = Form(None),
    dob: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    playerNationality: Optional[str] = Form(None),
    playerPhoto: Optional[UploadFile] = File(None),
    preferredPositionCategory: Optional[str] = Form(None),
    preferredPosition: Optional[str] = Form(None),
    otherPositions: Optional[List[str]] = Form(None),
    dominantFoot: Optional[str] = Form(None),
    height: Optional[int] = Form(None),
    weight: Optional[int] = Form(None),
    league: Optional[str] = Form(None),
    leagueClub: Optional[str] = Form(None),
    generalClub: Optional[str] = Form(None),
    customClub: Optional[str] = Form(None)
):
    try:
        # Only process player registrations for now
        if userType != "player":
            return templates.TemplateResponse("register.html", {
                "request": request,
                "error": f"{userType.capitalize()} registration coming soon!"
            })

        # Validate required fields
        if not all([firstName, lastName, email, password, confirmPassword]):
            return templates.TemplateResponse("register.html", {
                "request": request,
                "error": "All required fields must be filled"
            })

        # Validate password match
        if password != confirmPassword:
            return templates.TemplateResponse("register.html", {
                "request": request,
                "error": "Passwords do not match"
            })

        # Validate password length
        if len(password) < 6:
            return templates.TemplateResponse("register.html", {
                "request": request,
                "error": "Password must be at least 6 characters long"
            })

        # Check for duplicate users
        if users_collection:
            existing_user = users_collection.find_one({
                "$or": [
                    {"email": email.lower()},
                    {"$and": [
                        {"firstName": {"$regex": f"^{firstName}$", "$options": "i"}},
                        {"lastName": {"$regex": f"^{lastName}$", "$options": "i"}}
                    ]}
                ]
            })
            
            if existing_user:
                return templates.TemplateResponse("register.html", {
                    "request": request,
                    "error": "A user with these credentials already exists"
                })

        # Handle photo upload
        photo_filename = None
        if playerPhoto and playerPhoto.filename:
            # Check file size (200KB limit)
            photo_content = await playerPhoto.read()
            if len(photo_content) > 200 * 1024:  # 200KB
                return templates.TemplateResponse("register.html", {
                    "request": request,
                    "error": "Photo size must be 200KB or less"
                })
            
            # Save photo
            photo_filename = f"{email}_{playerPhoto.filename}"
            photo_path = uploads_dir / photo_filename
            with open(photo_path, "wb") as f:
                f.write(photo_content)

        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Determine club name
        club_name = None
        if leagueClub:
            club_name = leagueClub
        elif generalClub and generalClub != "not-available":
            club_name = generalClub
        elif customClub:
            club_name = customClub

        # Prepare user data
        user_data = {
            "userType": userType,
            "firstName": firstName,
            "middleName": middleName,
            "lastName": lastName,
            "email": email.lower(),
            "password": hashed_password,
            "dob": dob,
            "gender": gender,
            "nationality": playerNationality,
            "photo": photo_filename,
            "preferredPositionCategory": preferredPositionCategory,
            "preferredPosition": preferredPosition,
            "otherPositions": otherPositions or [],
            "dominantFoot": dominantFoot,
            "height": height,
            "weight": weight,
            "league": league,
            "club": club_name,
            "registeredAt": datetime.utcnow(),
            "status": "active"
        }

        # Save to MongoDB
        if users_collection:
            result = users_collection.insert_one(user_data)
            if result.inserted_id:
                return templates.TemplateResponse("register.html", {
                    "request": request,
                    "success": "Registration successful! Welcome to Enejistats."
                })
            else:
                return templates.TemplateResponse("register.html", {
                    "request": request,
                    "error": "Registration failed. Please try again."
                })
        else:
            return templates.TemplateResponse("register.html", {
                "request": request,
                "error": "Database connection error. Please try again later."
            })

    except Exception as e:
        print(f"Registration error: {e}")
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "An unexpected error occurred. Please try again."
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
