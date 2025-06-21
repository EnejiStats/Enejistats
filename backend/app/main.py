import os
from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException, Response, Cookie
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from typing import Optional, List
from pydantic import BaseModel
import json
import bcrypt
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv
from jose import JWTError, jwt
from datetime import datetime, timedelta
from bson.objectid import ObjectId

# Load environment variables
load_dotenv()

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Create uploads directory if needed
uploads_dir = Path("static/uploads")
uploads_dir.mkdir(parents=True, exist_ok=True)

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI")
if MONGO_URI and SECRET_KEY:
    try:
        client = MongoClient(MONGO_URI)
        db = client["enejistats"]
        players_collection = db["players"]
        contact_collection = db["contact_messages"]
        print("Connected to MongoDB")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        client = None
        db = None
        players_collection = None
        contact_collection = None
else:
    client = None
    db = None
    players_collection = None
    contact_collection = None
    print("Warning: MONGO_URI or SECRET_KEY not set. Using JSON file storage.")

# Pydantic model
class Player(BaseModel):
    player_id: str
    first_name: str
    middle_name: Optional[str] = ""
    last_name: str
    dob: str
    nationality: str
    preferred_position_category: str
    preferred_position: str
    club: str
    photo_url: str

# JWT helper functions
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

# JSON fallback save
def save_to_json(data):
    file = Path("registrations.json")
    if file.exists():
        with open(file, "r") as f:
            existing = json.load(f)
    else:
        existing = []
    existing.append(data)
    with open(file, "w") as f:
        json.dump(existing, f, indent=2)

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, access_token: str = Cookie(None)):
    if access_token and verify_token(access_token):
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def post_login(
    response: Response,
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    if players_collection is not None:
        user = players_collection.find_one({"email": email})
        if user and bcrypt.checkpw(password.encode(), user["password"].encode()):
            token = create_access_token({"sub": str(user["_id"])})
            res = RedirectResponse(url="/dashboard", status_code=302)
            res.set_cookie("access_token", token, httponly=True, max_age=3600)
            return res
        else:
            return templates.TemplateResponse("login.html", {
                "request": request,
                "message": "Invalid email or password."
            })
    else:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "message": "Database not available."
        })

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, access_token: str = Cookie(None)):
    user_id = verify_token(access_token)
    if not user_id or players_collection is None:
        return RedirectResponse(url="/login")

    user = players_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return RedirectResponse(url="/login")

    return templates.TemplateResponse("dashboard.html", {"request": request, "player": user})

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register_user(
    request: Request,
    firstName: str = Form(...),
    lastName: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    dob: str = Form(...),
    nationality: str = Form(...),
    preferredPositionCategory: str = Form(...),
    preferredPosition: str = Form(...),
    club: str = Form(...),
    playerPhoto: Optional[UploadFile] = File(None)
):
    try:
        # Check for duplicates
        if players_collection is not None:
            duplicate = players_collection.find_one({"email": email})
            if duplicate:
                return templates.TemplateResponse("register.html", {
                    "request": request,
                    "error": "Email already registered"
                })

        # Upload photo
        photo_filename = None
        if playerPhoto:
            content = await playerPhoto.read()
            photo_filename = f"{firstName.lower()}_{lastName.lower()}.jpg"
            with open(uploads_dir / photo_filename, "wb") as f:
                f.write(content)

        # Hash password
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        player_data = {
            "firstName": firstName,
            "lastName": lastName,
            "email": email,
            "password": hashed_pw,
            "dob": dob,
            "nationality": nationality,
            "preferredPositionCategory": preferredPositionCategory,
            "preferredPosition": preferredPosition,
            "club": club,
            "photo": photo_filename,
            "created_at": datetime.utcnow()
        }

        if players_collection is not None:
            players_collection.insert_one(player_data)
        else:
            save_to_json(player_data)

        return RedirectResponse(url="/success", status_code=303)

    except Exception as e:
        print(f"Registration error: {e}")
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "An unexpected error occurred. Please try again."
        })

@app.get("/success", response_class=HTMLResponse)
async def success_page():
    return HTMLResponse("""
    <html><body><h2>Registration successful!</h2><a href="/login">Login</a></body></html>
    """)

# Only run locally
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
