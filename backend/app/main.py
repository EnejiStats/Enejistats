
import os
from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pymongo
from pymongo import MongoClient
import bcrypt
from typing import Optional, List
import base64
from datetime import datetime
import json

app = FastAPI()

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DATABASE_NAME = "enejistats"

# Initialize MongoDB connection
try:
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    users_collection = db["users"]
    # Test the connection
    client.admin.command('ping')
    print("Connected to MongoDB successfully")
    MONGODB_AVAILABLE = True
except Exception as e:
    print(f"MongoDB connection error: {e}")
    print("Falling back to JSON file storage")
    client = None
    db = None
    users_collection = None
    MONGODB_AVAILABLE = False

# Templates setup
templates = Jinja2Templates(directory=".")

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head><title>Enejistats - Home</title></head>
        <body>
            <h1>Welcome to Enejistats</h1>
            <p><a href="/register">Register Here</a></p>
        </body>
    </html>
    """

@app.get("/register", response_class=HTMLResponse)
async def get_register(request: Request, message: str = None, success: str = None):
    try:
        with open("register.html", "r") as f:
            html_content = f.read()
        
        # Simple template replacement for messages
        if message:
            html_content = html_content.replace('{% if message %}', '').replace('{% endif %}', '').replace('{{ message }}', message)
        else:
            # Remove message block if no message
            start = html_content.find('{% if message %}')
            end = html_content.find('{% endif %}', start) + len('{% endif %}')
            if start != -1 and end != -1:
                html_content = html_content[:start] + html_content[end:]
        
        if success:
            html_content = html_content.replace('{% if success %}', '').replace('{{ success }}', success)
        else:
            # Remove success block if no success
            start = html_content.find('{% if success %}')
            end = html_content.find('{% endif %}', start) + len('{% endif %}')
            if start != -1 and end != -1:
                html_content = html_content[:start] + html_content[end:]
        
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html>
            <head><title>Register - Enejistats</title></head>
            <body>
                <h1>Registration Form</h1>
                <p>Error: register.html file not found</p>
                <p><a href="/">Back to Home</a></p>
            </body>
        </html>
        """)

def save_user_to_json(user_data):
    """Save user data to JSON file as fallback"""
    try:
        try:
            with open("users_data.json", "r") as f:
                users_data = json.load(f)
        except FileNotFoundError:
            users_data = []
        
        # Check if email exists
        if any(user.get('email') == user_data['email'] for user in users_data):
            return False, "Email already registered"
        
        # Convert datetime and bytes for JSON serialization
        json_user_data = user_data.copy()
        json_user_data['password'] = user_data['password'].decode('utf-8')
        json_user_data['registrationDate'] = user_data['registrationDate'].isoformat()
        
        users_data.append(json_user_data)
        
        with open("users_data.json", "w") as f:
            json.dump(users_data, f, indent=2)
        
        return True, "Success"
    except Exception as e:
        print(f"Error saving to JSON: {e}")
        return False, f"Error saving data: {str(e)}"

def save_user_to_mongodb(user_data):
    """Save user data to MongoDB"""
    try:
        # Check if email already exists
        existing_user = users_collection.find_one({'email': user_data['email']})
        if existing_user:
            return False, "Email already registered"
        
        # Insert user
        result = users_collection.insert_one(user_data)
        if result.inserted_id:
            return True, "Success"
        else:
            return False, "Failed to insert user"
    except Exception as e:
        print(f"MongoDB save error: {e}")
        return False, f"Database error: {str(e)}"

@app.post("/register")
async def register_user(
    userType: str = Form(...),
    firstName: Optional[str] = Form(None),
    middleName: Optional[str] = Form(None),
    lastName: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
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
    clubAssociation: Optional[str] = Form(None),
    club: Optional[str] = Form(None)
):
    try:
        print(f"Received registration request for userType: {userType}")
        
        # Handle different user types
        if userType in ["club", "scout"]:
            return RedirectResponse(
                url="/register?message=Registration for this user type is coming soon!",
                status_code=303
            )
        
        if userType != "player":
            return RedirectResponse(
                url="/register?message=Please select a valid user type.",
                status_code=303
            )
        
        # Validate required fields for player
        required_fields = {
            'firstName': firstName,
            'lastName': lastName,
            'email': email,
            'password': password,
            'dob': dob,
            'gender': gender,
            'playerNationality': playerNationality,
            'preferredPositionCategory': preferredPositionCategory,
            'dominantFoot': dominantFoot,
            'height': height,
            'weight': weight,
            'league': league,
            'clubAssociation': clubAssociation
        }
        
        missing_fields = [field for field, value in required_fields.items() if not value]
        if missing_fields:
            return RedirectResponse(
                url=f"/register?message=Missing required fields: {', '.join(missing_fields)}",
                status_code=303
            )
        
        # Validate email format
        if '@' not in email or '.' not in email.split('@')[-1]:
            return RedirectResponse(
                url="/register?message=Please enter a valid email address.",
                status_code=303
            )
        
        # Validate password length
        if len(password) < 6:
            return RedirectResponse(
                url="/register?message=Password must be at least 6 characters long.",
                status_code=303
            )
        
        # Handle photo upload
        photo_data = None
        if playerPhoto and playerPhoto.filename:
            # Check file size (20KB = 20,480 bytes)
            contents = await playerPhoto.read()
            if len(contents) > 20480:
                return RedirectResponse(
                    url="/register?message=Photo size must be 20KB or less.",
                    status_code=303
                )
            
            # Convert to base64 for storage
            photo_data = base64.b64encode(contents).decode('utf-8')
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Determine club based on league
        selected_club = None
        if league in ['npfl', 'nnl1', 'nnl2', 'academy']:
            selected_club = leagueClub
        elif league in ['street', 'university']:
            selected_club = generalClub
        
        # Create user data
        user_data = {
            'userType': userType,
            'firstName': firstName,
            'middleName': middleName,
            'lastName': lastName,
            'email': email,
            'password': hashed_password,
            'dob': dob,
            'gender': gender,
            'nationality': playerNationality,
            'photo': photo_data,
            'preferredPositionCategory': preferredPositionCategory,
            'preferredPosition': preferredPosition,
            'otherPositions': otherPositions or [],
            'dominantFoot': dominantFoot,
            'height': height,
            'weight': weight,
            'league': league,
            'club': selected_club,
            'clubAssociation': clubAssociation,
            'associatedClub': club if clubAssociation == 'yes' else None,
            'registrationDate': datetime.utcnow(),
            'active': True
        }
        
        # Save user data
        if MONGODB_AVAILABLE:
            success, message = save_user_to_mongodb(user_data)
        else:
            success, message = save_user_to_json(user_data)
        
        if success:
            print("User registered successfully")
            return RedirectResponse(
                url="/register?success=Registration successful! Welcome to Enejistats.",
                status_code=303
            )
        else:
            print(f"Registration failed: {message}")
            return RedirectResponse(
                url=f"/register?message={message}",
                status_code=303
            )
    
    except Exception as e:
        print(f"Registration error: {e}")
        return RedirectResponse(
            url="/register?message=An error occurred during registration. Please try again.",
            status_code=303
        )

@app.get("/health")
async def health_check():
    """Health check endpoint to verify MongoDB connection"""
    status = {
        "status": "healthy",
        "mongodb": "connected" if MONGODB_AVAILABLE else "disconnected",
        "fallback": "json_file" if not MONGODB_AVAILABLE else "none"
    }
    return status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
