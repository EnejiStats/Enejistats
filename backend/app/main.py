
import os
from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from typing import Optional
import bcrypt
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import base64

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

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://enejistats:BCC0706%24%24@cluster1.wlmimug.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1")
SECRET_KEY = os.getenv("SECRET_KEY", "s2M7WkZaXt0bYOIQ5oEPz7Ha2v2kqCDe3F3uU4xKgPH7NQvplg4fb9hzKWbTynh2")

try:
    client = MongoClient(MONGO_URI)
    db = client.enejistats_db
    users_collection = db.users
    print("Connected to MongoDB successfully")
except Exception as e:
    print(f"MongoDB connection error: {e}")
    client = None
    db = None
    users_collection = None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register_user(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    state: str = Form(...),
    gender: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    photo: UploadFile = File(...)
):
    try:
        # Validate passwords match
        if password != confirm_password:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Passwords do not match"}
            )
        
        # Check if MongoDB is available
        if not users_collection:
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": "Database connection error"}
            )
        
        # Check if user already exists
        existing_user = users_collection.find_one({
            "$or": [
                {"email": email.lower()},
                {"full_name": full_name.lower()}
            ]
        })
        
        if existing_user:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "User with this email or name already exists"}
            )
        
        # Validate photo size (200KB = 204800 bytes)
        photo_content = await photo.read()
        if len(photo_content) > 204800:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Photo size must be less than 200KB"}
            )
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Encode photo as base64 for storage
        photo_base64 = base64.b64encode(photo_content).decode('utf-8')
        
        # Create user document
        user_doc = {
            "full_name": full_name.lower(),
            "email": email.lower(),
            "phone": phone,
            "state": state,
            "gender": gender,
            "password": hashed_password,
            "photo": photo_base64,
            "photo_filename": photo.filename,
            "created_at": datetime.utcnow()
        }
        
        # Insert user into MongoDB
        result = users_collection.insert_one(user_doc)
        
        if result.inserted_id:
            return JSONResponse(
                status_code=200,
                content={"success": True, "message": "Registration successful!"}
            )
        else:
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": "Failed to save user data"}
            )
            
    except Exception as e:
        print(f"Registration error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "An unexpected error occurred. Please try again."}
        )

@app.get("/check-user")
async def check_user(email: str = None, full_name: str = None):
    try:
        if not users_collection:
            return JSONResponse(content={"exists": False})
        
        query = {}
        if email:
            query["email"] = email.lower()
        if full_name:
            query["full_name"] = full_name.lower()
        
        if query:
            existing_user = users_collection.find_one(query)
            return JSONResponse(content={"exists": bool(existing_user)})
        
        return JSONResponse(content={"exists": False})
    except Exception as e:
        print(f"Check user error: {e}")
        return JSONResponse(content={"exists": False})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
