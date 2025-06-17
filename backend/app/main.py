
import os
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
from dotenv import load_dotenv
from typing import Optional, List
import shutil
import bcrypt

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up template directory
templates = Jinja2Templates(directory="templates")

# Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI")
if MONGO_URI:
    client = MongoClient(MONGO_URI)
    db = client["enejistats"]
    players_collection = db["players"]
else:
    # Fallback for development without MongoDB
    client = None
    db = None
    players_collection = None
    print("Warning: MONGO_URI not set. MongoDB features will be disabled.")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # Try to use templates first, fallback to direct HTML file
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except:
        with open("index.html", "r") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)

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

@app.post("/login", response_class=HTMLResponse)
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

@app.get("/register", response_class=HTMLResponse)
async def get_register(request: Request):
    try:
        return templates.TemplateResponse("register.html", {"request": request})
    except:
        with open("index.html", "r") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)

@app.post("/register")
async def register_user(
    request: Request,
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
    # Process the registration data
    registration_data = {
        "userType": userType,
        "firstName": firstName,
        "middleName": middleName,
        "lastName": lastName,
        "email": email,
        "dob": dob,
        "gender": gender,
        "playerNationality": playerNationality,
        "preferredPositionCategory": preferredPositionCategory,
        "preferredPosition": preferredPosition,
        "otherPositions": otherPositions,
        "dominantFoot": dominantFoot,
        "height": height,
        "weight": weight,
        "league": league,
        "leagueClub": leagueClub,
        "generalClub": generalClub,
        "clubAssociation": clubAssociation,
        "club": club
    }
    
    # Handle file upload
    photo_filename = None
    if playerPhoto and playerPhoto.filename:
        # Create uploads directory if it doesn't exist
        upload_dir = "static/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate filename
        if firstName and lastName:
            photo_filename = f"{firstName.lower()}_{lastName.lower()}.jpg"
        else:
            photo_filename = playerPhoto.filename
        
        # Save the uploaded file
        file_path = os.path.join(upload_dir, photo_filename)
        with open(file_path, "wb") as buffer:
            content = await playerPhoto.read()
            buffer.write(content)
        
        registration_data["playerPhoto"] = photo_filename

    # If MongoDB is available and this is a player registration, save to database
    if players_collection and userType == 'player':
        try:
            # Hash the password before storing
            if password:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                registration_data["password"] = hashed_password.decode('utf-8')
            
            # Determine selected club
            selected_club = leagueClub or generalClub or club
            registration_data["club"] = selected_club
            
            # Rename fields for consistency
            if playerNationality:
                registration_data["nationality"] = playerNationality
                del registration_data["playerNationality"]
            
            if photo_filename:
                registration_data["photo"] = photo_filename
                del registration_data["playerPhoto"]
            
            # Remove None values and non-database fields
            clean_data = {k: v for k, v in registration_data.items() 
                         if v is not None and k not in ['userType']}
            
            # Save to MongoDB
            players_collection.insert_one(clean_data)
            
            # Return success page or redirect
            return RedirectResponse(url="/success", status_code=303)
            
        except Exception as e:
            print(f"Database error: {e}")
            # Continue with regular response if database fails
    
    # For non-player registrations or when MongoDB is not available
    print("Registration data received:", registration_data)
    
    # Return JSON response for API compatibility
    return {"message": "Registration successful", "data": registration_data}

@app.get("/success", response_class=HTMLResponse)
async def registration_success():
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
            .success-button { display: inline-block; margin-top: 1rem; padding: 0.75rem 1.5rem; background-color: #004aad; color: white; text-decoration: none; border-radius: 6px; }
        </style>
    </head>
    <body>
        <header>
            <h1>Enejistats</h1>
            <nav>
                <a href="/">Home</a>
                <a href="/leaderboard">Leaderboard</a>
                <a href="/">Register</a>
                <a href="/stats/browse">Browse</a>
            </nav>
        </header>
        <main>
            <h2>Registration Successful!</h2>
            <p>Thank you for registering with Enejistats. Your registration has been submitted successfully.</p>
            <a href="/" class="success-button">Back to Registration</a>
            <a href="/login" class="success-button">Login</a>
        </main>
        <footer>
            <p>&copy; 2025 Enejistats</p>
        </footer>
    </body>
    </html>
    """)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
