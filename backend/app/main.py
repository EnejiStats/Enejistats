
import os
from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from typing import Optional, List
import json
import bcrypt
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv

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

# MongoDB setup with fallback to JSON
MONGO_URI = os.getenv("MONGO_URI")
if MONGO_URI:
    try:
        client = MongoClient(MONGO_URI)
        db = client["enejistats"]
        players_collection = db["players"]
        print("Connected to MongoDB")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        client = None
        db = None
        players_collection = None
else:
    client = None
    db = None
    players_collection = None
    print("Warning: MONGO_URI not set. Using JSON file storage.")

# Helper function to save to JSON (fallback when MongoDB is not available)
def save_to_json(data):
    registrations_file = Path("registrations.json")
    if registrations_file.exists():
        with open(registrations_file, "r") as f:
            registrations = json.load(f)
    else:
        registrations = []
    
    registrations.append(data)
    
    with open(registrations_file, "w") as f:
        json.dump(registrations, f, indent=2)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the registration form as home page"""
    try:
        return templates.TemplateResponse("register.html", {"request": request})
    except Exception:
        # Fallback if templates don't work
        try:
            with open("register.html", "r") as f:
                html_content = f.read()
            return HTMLResponse(content=html_content)
        except Exception:
            raise HTTPException(status_code=404, detail="Registration page not found")

@app.get("/register", response_class=HTMLResponse)
async def get_register_form(request: Request):
    """Serve the registration form"""
    return await home(request)

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/stats/player", response_class=HTMLResponse)
async def stats_player(request: Request):
    return templates.TemplateResponse("player_dashboard.html", {"request": request})

@app.get("/stats/browse", response_class=HTMLResponse)
async def stats_browse(request: Request):
    return templates.TemplateResponse("browse.html", {"request": request})

@app.get("/leaderboard", response_class=HTMLResponse)
async def leaderboard(request: Request):
    return templates.TemplateResponse("leaderboard.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def post_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    if not players_collection:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "message": "Database not available."
        })

    user = players_collection.find_one({"email": email})

    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "message": "Invalid email or password."
        })

    stored_password = user["password"]
    if not bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "message": "Invalid email or password."
        })

    # Success
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "player": user,
        "message": "Login successful!"
    })

@app.post("/register")
async def register_user(
    request: Request,
    userType: str = Form(...),
    # Player fields
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
    """Handle user registration"""
    
    try:
        # Basic validation
        if userType not in ["player", "club", "scout"]:
            return JSONResponse(
                content={"success": False, "message": "Invalid user type"},
                status_code=400
            )
        
        # Handle player registration
        if userType == "player":
            # Validate required fields
            required_fields = {
                "firstName": firstName,
                "lastName": lastName,
                "email": email,
                "password": password,
                "dob": dob,
                "gender": gender,
                "playerNationality": playerNationality,
                "preferredPositionCategory": preferredPositionCategory,
                "preferredPosition": preferredPosition,
                "dominantFoot": dominantFoot,
                "height": height,
                "weight": weight,
                "league": league,
                "clubAssociation": clubAssociation
            }
            
            missing_fields = [field for field, value in required_fields.items() if not value]
            if missing_fields:
                return JSONResponse(
                    content={"success": False, "message": f"Missing required fields: {', '.join(missing_fields)}"},
                    status_code=400
                )
            
            # Handle photo upload
            photo_filename = None
            if playerPhoto and playerPhoto.filename:
                # Validate file size (20KB limit)
                content = await playerPhoto.read()
                if len(content) > 20 * 1024:  # 20KB
                    return JSONResponse(
                        content={"success": False, "message": "Photo size must be 20KB or less"},
                        status_code=400
                    )
                
                # Generate filename
                if firstName and lastName:
                    photo_filename = f"{firstName.lower()}_{lastName.lower()}.jpg"
                else:
                    photo_filename = f"{email}_{playerPhoto.filename}"
                
                # Save the file
                file_path = uploads_dir / photo_filename
                with open(file_path, "wb") as buffer:
                    buffer.write(content)
            
            # Hash password
            hashed_password = None
            if password:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Determine selected club
            selected_club = leagueClub or generalClub or club
            
            # Prepare registration data
            registration_data = {
                "userType": userType,
                "firstName": firstName,
                "middleName": middleName,
                "lastName": lastName,
                "email": email,
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
                "club": selected_club,
                "clubAssociation": clubAssociation
            }
            
            # Save to MongoDB if available, otherwise save to JSON
            if players_collection:
                try:
                    # Remove userType and None values for database
                    clean_data = {k: v for k, v in registration_data.items() 
                                 if v is not None and k != 'userType'}
                    
                    players_collection.insert_one(clean_data)
                    return RedirectResponse(url="/success", status_code=303)
                    
                except Exception as e:
                    print(f"MongoDB error: {e}")
                    # Fall back to JSON storage
                    save_to_json(registration_data)
                    return JSONResponse(
                        content={"success": True, "message": "Player registration successful! (Saved to backup)"},
                        status_code=200
                    )
            else:
                # Save to JSON file
                save_to_json(registration_data)
                return JSONResponse(
                    content={"success": True, "message": "Player registration successful!"},
                    status_code=200
                )
        
        # Handle club and scout registrations (coming soon)
        elif userType in ["club", "scout"]:
            return JSONResponse(
                content={"success": False, "message": f"{userType.title()} registration coming soon!"},
                status_code=400
            )
        
    except Exception as e:
        print(f"Registration error: {str(e)}")
        return JSONResponse(
            content={"success": False, "message": "An error occurred during registration"},
            status_code=500
        )

@app.get("/success", response_class=HTMLResponse)
async def registration_success():
    """Show registration success page"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Registration Success | Enejistats</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { box-sizing: border-box; }
            body { margin: 0; font-family: 'Segoe UI', sans-serif; background-color: #f5f7fa; color: #333; }
            header, footer { background-color: #1e1e2f; color: white; padding: 1rem; text-align: center; }
            nav { margin-top: 0.5rem; }
            nav a { color: white; margin: 0 0.75rem; text-decoration: none; font-weight: 500; }
            main { max-width: 800px; margin: 2rem auto; padding: 2rem; background: white; border-radius: 8px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); text-align: center; }
            h2 { color: #004aad; }
            .success-button { display: inline-block; margin: 0.5rem; padding: 0.75rem 1.5rem; background-color: #004aad; color: white; text-decoration: none; border-radius: 6px; }
        </style>
    </head>
    <body>
        <header>
            <h1>Enejistats</h1>
            <nav>
                <a href="/">Home</a>
                <a href="/leaderboard">Leaderboard</a>
                <a href="/register">Register</a>
                <a href="/stats/browse">Browse</a>
            </nav>
        </header>
        <main>
            <h2>Registration Successful!</h2>
            <p>Thank you for registering with Enejistats. Your registration has been submitted successfully.</p>
            <a href="/register" class="success-button">Register Another Player</a>
            <a href="/login" class="success-button">Login</a>
        </main>
        <footer>
            <p>&copy; 2025 Enejistats</p>
        </footer>
    </body>
    </html>
    """)

@app.get("/registrations")
async def get_registrations():
    """Get all registrations (for testing purposes)"""
    if players_collection:
        try:
            registrations = list(players_collection.find({}, {"_id": 0}))
            return {"registrations": registrations, "source": "mongodb"}
        except Exception as e:
            print(f"MongoDB query error: {e}")
    
    # Fallback to JSON file
    registrations_file = Path("registrations.json")
    if registrations_file.exists():
        with open(registrations_file, "r") as f:
            registrations = json.load(f)
        return {"registrations": registrations, "source": "json"}
    
    return {"registrations": [], "source": "none"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
