
import os
from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException, Response, Cookie
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.requests import Request
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import json
import bcrypt
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv
from jose import JWTError, jwt
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import uuid

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

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key_for_development")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# MongoDB setup with fallback to JSON
MONGO_URI = os.getenv("MONGO_URI")
if MONGO_URI and SECRET_KEY:
    try:
        client = MongoClient(MONGO_URI)
        db = client["enejistats"]
        players_collection = db["players"]
        contact_collection = db["contact_messages"]
        matches_collection = db["matches"]
        match_stats_collection = db["match_stats"]
        player_stats_collection = db["player_stats"]
        print("Connected to MongoDB")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        client = None
        db = None
        players_collection = None
        contact_collection = None
        matches_collection = None
        match_stats_collection = None
        player_stats_collection = None
else:
    client = None
    db = None
    players_collection = None
    contact_collection = None
    matches_collection = None
    match_stats_collection = None
    player_stats_collection = None
    print("Warning: MONGO_URI or SECRET_KEY not set. Using JSON file storage.")

# Pydantic Models
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

class MatchStats(BaseModel):
    match_id: str
    player_id: str
    goals: int = 0
    shots_on: int = 0
    shots_off: int = 0
    short_passes_successful: int = 0
    short_passes_unsuccessful: int = 0
    long_passes_successful: int = 0
    long_passes_unsuccessful: int = 0
    crosses_successful: int = 0
    crosses_unsuccessful: int = 0
    interceptions: int = 0
    tackles: int = 0
    clearances: int = 0
    gk_saves: int = 0
    yellow_cards: int = 0
    red_cards: int = 0
    fouls: int = 0
    offsides: int = 0
    minutes_played: int = 90
    position_played: str = ""
    time_in: int = 0
    time_out: int = 90

# Rating System Calculator
class PlayerRatingCalculator:
    def __init__(self):
        # Position weights for different stats
        self.position_weights = {
            "goalkeeper": {
                "gk_saves": 0.30,
                "goals_conceded": -0.25,
                "clearances": 0.15,
                "distribution": 0.20,
                "discipline": -0.10
            },
            "defender": {
                "tackles": 0.25,
                "clearances": 0.20,
                "interceptions": 0.20,
                "passes": 0.15,
                "goals": 0.10,
                "discipline": -0.10
            },
            "midfielder": {
                "passes": 0.30,
                "assists": 0.20,
                "goals": 0.15,
                "tackles": 0.15,
                "interceptions": 0.10,
                "discipline": -0.10
            },
            "attacker": {
                "goals": 0.35,
                "assists": 0.20,
                "shots_on_target": 0.20,
                "passes": 0.15,
                "discipline": -0.10
            }
        }

    def calculate_rating(self, stats: Dict[str, Any], position_category: str) -> float:
        """Calculate WhoScored-style rating based on position and stats"""
        base_rating = 6.0  # Starting rating
        position_category = position_category.lower()
        
        if position_category not in self.position_weights:
            position_category = "midfielder"  # Default fallback
        
        weights = self.position_weights[position_category]
        
        # Calculate individual component scores
        components = {}
        
        # Goals component
        if "goals" in weights:
            goals_score = min(stats.get("goals", 0) * 0.8, 2.0)
            components["goals"] = goals_score * weights["goals"]
        
        # Assists component (derived from key passes and successful crosses)
        if "assists" in weights:
            assists_score = min(stats.get("assists", 0) * 0.6, 1.5)
            components["assists"] = assists_score * weights["assists"]
        
        # Passing component
        if "passes" in weights:
            total_passes = stats.get("short_passes_successful", 0) + stats.get("long_passes_successful", 0)
            total_attempted = total_passes + stats.get("short_passes_unsuccessful", 0) + stats.get("long_passes_unsuccessful", 0)
            pass_accuracy = (total_passes / max(total_attempted, 1)) * 100
            pass_score = (pass_accuracy / 100) * 2.0 + (total_passes / 50)
            components["passes"] = min(pass_score, 2.5) * weights["passes"]
        
        # Defensive components
        if "tackles" in weights:
            tackle_score = min(stats.get("tackles", 0) * 0.3, 2.0)
            components["tackles"] = tackle_score * weights["tackles"]
        
        if "interceptions" in weights:
            interception_score = min(stats.get("interceptions", 0) * 0.25, 1.5)
            components["interceptions"] = interception_score * weights["interceptions"]
        
        if "clearances" in weights:
            clearance_score = min(stats.get("clearances", 0) * 0.2, 1.5)
            components["clearances"] = clearance_score * weights["clearances"]
        
        # Goalkeeper specific
        if "gk_saves" in weights:
            saves_score = min(stats.get("gk_saves", 0) * 0.15, 2.5)
            components["gk_saves"] = saves_score * weights["gk_saves"]
        
        if "distribution" in weights:
            total_passes = stats.get("short_passes_successful", 0) + stats.get("long_passes_successful", 0)
            distribution_score = min(total_passes * 0.05, 1.5)
            components["distribution"] = distribution_score * weights["distribution"]
        
        # Shooting accuracy for attackers
        if "shots_on_target" in weights:
            shots_on = stats.get("shots_on", 0)
            shots_total = shots_on + stats.get("shots_off", 0)
            shot_accuracy = (shots_on / max(shots_total, 1)) * 100 if shots_total > 0 else 0
            shot_score = (shots_on * 0.3) + (shot_accuracy / 100)
            components["shots_on_target"] = min(shot_score, 2.0) * weights["shots_on_target"]
        
        # Discipline component (negative impact)
        if "discipline" in weights:
            discipline_penalty = (stats.get("yellow_cards", 0) * 0.3) + (stats.get("red_cards", 0) * 1.5) + (stats.get("fouls", 0) * 0.1)
            components["discipline"] = discipline_penalty * weights["discipline"]
        
        # Calculate bonus for non-natural position contribution
        position_bonus = 0.0
        natural_position = stats.get("natural_position", "").lower()
        played_position = stats.get("position_played", "").lower()
        
        if natural_position and played_position and natural_position != played_position:
            # Bonus for playing out of position successfully
            performance_multiplier = sum(components.values()) / len(components) if components else 0
            if performance_multiplier > 0.5:  # Good performance threshold
                position_bonus = 0.3
        
        # Sum all components
        total_component_score = sum(components.values()) + position_bonus
        
        # Calculate final rating
        final_rating = base_rating + total_component_score
        
        # Cap the rating at 10.0 and minimum at 1.0
        final_rating = max(1.0, min(final_rating, 10.0))
        
        return round(final_rating, 1)

# Initialize rating calculator
rating_calculator = PlayerRatingCalculator()

# JWT Helper Functions
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

# Helper function to save to JSON (fallback when MongoDB is not available)
def save_to_json(data, filename="registrations.json"):
    file_path = Path(filename)
    if file_path.exists():
        with open(file_path, "r") as f:
            existing_data = json.load(f)
    else:
        existing_data = []
    
    existing_data.append(data)
    
    with open(file_path, "w") as f:
        json.dump(existing_data, f, indent=2)

# Routes

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the home page"""
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception:
        try:
            return templates.TemplateResponse("register.html", {"request": request})
        except Exception:
            raise HTTPException(status_code=404, detail="Home page not found")

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """Serve the about page"""
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    """Serve the contact page"""
    return templates.TemplateResponse("contact.html", {"request": request})

@app.get("/leaderboard", response_class=HTMLResponse)
async def leaderboard(request: Request):
    """Serve the leaderboard page"""
    return templates.TemplateResponse("leaderboard.html", {"request": request})

@app.get("/browse", response_class=HTMLResponse)
async def browse(request: Request):
    """Serve the browse page"""
    return templates.TemplateResponse("browse.html", {"request": request})

@app.get("/stats-area", response_class=HTMLResponse)
async def stats_area(request: Request):
    """Serve the stats area page with tabbed access to Player and Browse."""
    return templates.TemplateResponse("stats-area.html", {"request": request})

@app.get("/stats", response_class=HTMLResponse)
async def stats(request: Request):
    """Serve the stats page"""
    return templates.TemplateResponse("stats_area.html", {"request": request})

@app.get("/player", response_class=HTMLResponse)
async def player(request: Request):
    """Serve the player page"""
    return templates.TemplateResponse("player.html", {"request": request})

@app.get("/stats/browse", response_class=HTMLResponse)
async def stats_browse(request: Request):
    """Serve the stats browse page"""
    return templates.TemplateResponse("browse.html", {"request": request})

@app.get("/stats/player", response_class=HTMLResponse)
async def stats_player(request: Request):
    """Serve the stats player page"""
    return templates.TemplateResponse("player.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def get_register_form(request: Request):
    """Serve the registration form"""
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request, access_token: str = Cookie(None)):
    """Serve the login page"""
    if access_token and verify_token(access_token):
        return RedirectResponse(url="/player-dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/player-dashboard", response_class=HTMLResponse)
async def player_dashboard(request: Request, access_token: str = Cookie(None)):
    """Serve the player dashboard page with session check"""
    user_id = verify_token(access_token)
    if not user_id:
        return RedirectResponse(url="/login")

    if players_collection is None:
        return RedirectResponse(url="/login")

    user = players_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return RedirectResponse(url="/login")

    # Get player's match statistics
    player_stats = []
    if player_stats_collection:
        stats_cursor = player_stats_collection.find({"player_id": str(user["_id"])}).sort("match_date", -1).limit(10)
        player_stats = list(stats_cursor)

    return templates.TemplateResponse("player-dashboard.html", {
        "request": request,
        "player": user,
        "player_stats": player_stats
    })

@app.get("/scout-widget", response_class=HTMLResponse)
async def scout_widget(request: Request, access_token: str = Cookie(None)):
    """Serve the scout widget page"""
    user_id = verify_token(access_token)
    if not user_id:
        return RedirectResponse(url="/login")

    # Get all players for dropdown
    all_players = []
    if players_collection:
        players_cursor = players_collection.find({}, {"firstName": 1, "lastName": 1, "club": 1, "preferredPosition": 1})
        all_players = list(players_cursor)

    return templates.TemplateResponse("scout-widget.html", {
        "request": request,
        "players": all_players
    })

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, access_token: str = Cookie(None)):
    """Serve the dashboard page with authentication"""
    return RedirectResponse(url="/player-dashboard")

@app.get("/logout")
async def logout():
    """Handle user logout"""
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response

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
            <a href="/login" class="success-button">Login to Dashboard</a>
            <a href="/register" class="success-button">Register Another Player</a>
        </main>
        <footer>
            <p>&copy; 2025 Enejistats</p>
        </footer>
    </body>
    </html>
    """)

# API Routes

@app.get("/api/players")
async def get_players():
    """Get all players for dropdown selection"""
    if players_collection:
        players_cursor = players_collection.find({}, {
            "firstName": 1, "lastName": 1, "club": 1, 
            "preferredPosition": 1, "preferredPositionCategory": 1
        })
        players = list(players_cursor)
        for player in players:
            player["_id"] = str(player["_id"])
        return {"players": players}
    return {"players": []}

@app.get("/api/leagues")
async def get_leagues():
    """Get available leagues"""
    leagues = [
        {"id": "npfl", "name": "Nigerian Professional Football League"},
        {"id": "nnl1", "name": "Nigerian National League One"},
        {"id": "nnl2", "name": "Nigerian National League Two"},
        {"id": "academy", "name": "Academy League"},
        {"id": "street", "name": "Street League"},
        {"id": "university", "name": "University League"}
    ]
    return {"leagues": leagues}

@app.get("/api/teams/{league_id}")
async def get_teams_by_league(league_id: str):
    """Get teams by league"""
    league_teams = {
        "npfl": [
            "Enyimba FC", "Kano Pillars", "Rivers United", "Plateau United", 
            "Shooting Stars SC", "3SC Ibadan", "Akwa United", "Lobi Stars"
        ],
        "nnl1": [
            "Gombe United", "El-Kanemi Warriors", "ABS FC", "Insurance FC"
        ],
        "nnl2": [
            "Confluence Stars", "Ottasolo FC", "Beyond Limits", "Mighty Jets"
        ],
        "academy": [
            "Pepsi Football Academy", "36 Lion FC Academy", "Right to Dream Academy"
        ]
    }
    teams = league_teams.get(league_id, [])
    return {"teams": [{"id": team.lower().replace(" ", "-"), "name": team} for team in teams]}

@app.post("/api/submit-match-stats")
async def submit_match_stats(request: Request):
    """Submit match statistics and calculate rating"""
    try:
        data = await request.json()
        
        # Generate match ID if not provided
        match_id = data.get("match_id", str(uuid.uuid4()))
        
        # Calculate rating based on stats and position
        stats = {
            "goals": data.get("goals", 0),
            "shots_on": data.get("shots_on", 0),
            "shots_off": data.get("shots_off", 0),
            "short_passes_successful": data.get("short_passes_successful", 0),
            "short_passes_unsuccessful": data.get("short_passes_unsuccessful", 0),
            "long_passes_successful": data.get("long_passes_successful", 0),
            "long_passes_unsuccessful": data.get("long_passes_unsuccessful", 0),
            "crosses_successful": data.get("crosses_successful", 0),
            "crosses_unsuccessful": data.get("crosses_unsuccessful", 0),
            "interceptions": data.get("interceptions", 0),
            "tackles": data.get("tackles", 0),
            "clearances": data.get("clearances", 0),
            "gk_saves": data.get("gk_saves", 0),
            "yellow_cards": data.get("yellow_cards", 0),
            "red_cards": data.get("red_cards", 0),
            "fouls": data.get("fouls", 0),
            "offsides": data.get("offsides", 0),
            "minutes_played": data.get("minutes_played", 90),
            "position_played": data.get("position_played", ""),
            "natural_position": data.get("natural_position", "")
        }
        
        position_category = data.get("position_category", "midfielder")
        rating = rating_calculator.calculate_rating(stats, position_category)
        
        # Prepare match stats data
        match_stats_data = {
            "match_id": match_id,
            "player_id": data.get("player_id"),
            "match_date": data.get("match_date"),
            "home_team": data.get("home_team"),
            "away_team": data.get("away_team"),
            "league": data.get("league"),
            "performance_rating": rating,
            "stats": stats,
            "created_at": datetime.utcnow()
        }
        
        # Save to database
        if match_stats_collection:
            match_stats_collection.insert_one(match_stats_data)
        else:
            save_to_json(match_stats_data, "match_stats.json")
        
        return {
            "success": True,
            "match_id": match_id,
            "rating": rating,
            "message": "Match statistics submitted successfully"
        }
        
    except Exception as e:
        print(f"Error submitting match stats: {e}")
        return JSONResponse(
            content={"success": False, "message": f"Error: {str(e)}"},
            status_code=500
        )

@app.post("/api/update-player-bio")
async def update_player_bio(request: Request):
    """Update player bio information"""
    try:
        data = await request.json()
        player_id = data.get("player_id")
        
        if not player_id:
            return JSONResponse(
                content={"success": False, "message": "Player ID required"},
                status_code=400
            )
        
        update_data = {
            "bio": data.get("bio", ""),
            "updated_at": datetime.utcnow()
        }
        
        if players_collection:
            result = players_collection.update_one(
                {"_id": ObjectId(player_id)},
                {"$set": update_data}
            )
            if result.modified_count > 0:
                return {"success": True, "message": "Bio updated successfully"}
        
        return JSONResponse(
            content={"success": False, "message": "Failed to update bio"},
            status_code=500
        )
        
    except Exception as e:
        return JSONResponse(
            content={"success": False, "message": f"Error: {str(e)}"},
            status_code=500
        )

@app.post("/api/update-player-awards")
async def update_player_awards(request: Request):
    """Update player awards and achievements"""
    try:
        data = await request.json()
        player_id = data.get("player_id")
        
        if not player_id:
            return JSONResponse(
                content={"success": False, "message": "Player ID required"},
                status_code=400
            )
        
        update_data = {
            "awards": data.get("awards", []),
            "achievements": data.get("achievements", []),
            "updated_at": datetime.utcnow()
        }
        
        if players_collection:
            result = players_collection.update_one(
                {"_id": ObjectId(player_id)},
                {"$set": update_data}
            )
            if result.modified_count > 0:
                return {"success": True, "message": "Awards updated successfully"}
        
        return JSONResponse(
            content={"success": False, "message": "Failed to update awards"},
            status_code=500
        )
        
    except Exception as e:
        return JSONResponse(
            content={"success": False, "message": f"Error: {str(e)}"},
            status_code=500
        )

@app.get("/registrations")
async def get_registrations():
    """Get all registrations (for testing purposes)"""
    if players_collection is not None:
        try:
            registrations = list(players_collection.find({}, {"_id": 0}))
            return {"registrations": registrations, "source": "mongodb"}
        except Exception as e:
            print(f"MongoDB query error: {e}")
    
    registrations_file = Path("registrations.json")
    if registrations_file.exists():
        with open(registrations_file, "r") as f:
            registrations = json.load(f)
        return {"registrations": registrations, "source": "json"}
    
    return {"registrations": [], "source": "none"}

@app.post("/login")
async def post_login(
    response: Response,
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    """Handle user login"""
    if players_collection is None:
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

    token = create_access_token({"sub": str(user["_id"])})
    res = RedirectResponse(url="/player-dashboard", status_code=302)
    res.set_cookie("access_token", token, httponly=True, max_age=3600)
    return res

@app.post("/submit-contact")
async def submit_contact(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...)
):
    """Handle contact form submission"""
    contact_data = {
        "name": name,
        "email": email,
        "message": message,
        "created_at": datetime.utcnow()
    }
    
    if contact_collection is not None:
        try:
            contact_collection.insert_one(contact_data)
        except Exception as e:
            print(f"Failed to save contact message: {e}")
    
    return templates.TemplateResponse("contact.html", {"request": request, "success": True})

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
    customClub: Optional[str] = Form(None),
    # Legacy API fields for backward compatibility
    club: Optional[str] = Form(None),
    player_id: Optional[str] = Form(None),
    first_name: Optional[str] = Form(None),
    middle_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    nationality: Optional[str] = Form(None),
    preferred_position_category: Optional[str] = Form(None),
    preferred_position: Optional[str] = Form(None),
    photo_url: Optional[str] = Form(None)
):
    """Handle both web form registration and API registration"""
    
    try:
        # Check if this is an API call (legacy support)
        is_api_call = bool(player_id and first_name and last_name)
        
        if is_api_call:
            # Handle API registration
            new_player = {
                "player_id": player_id,
                "firstName": first_name,
                "middleName": middle_name or "",
                "lastName": last_name,
                "dob": dob,
                "nationality": nationality,
                "preferredPositionCategory": preferred_position_category,
                "preferredPosition": preferred_position,
                "club": club,
                "photo": photo_url,
                "created_at": datetime.utcnow()
            }
            
            try:
                if players_collection is not None:
                    players_collection.insert_one(new_player.copy())
                else:
                    save_to_json(new_player)
                
                return JSONResponse(content={
                    "success": True, 
                    "message": "Player registered successfully via API",
                    "player": new_player
                })
            except Exception as e:
                print(f"API registration error: {e}")
                return JSONResponse(content={
                    "success": False,
                    "message": f"Registration failed: {str(e)}"
                }, status_code=500)
        
        # Handle web form registration
        if userType not in ["player", "club", "scout"]:
            return templates.TemplateResponse("register.html", {
                "request": request,
                "error": "Invalid user type selected"
            })
        
        if userType == "player":
            # Validate required fields
            if not firstName or not lastName or not email or not password:
                return templates.TemplateResponse("register.html", {
                    "request": request,
                    "error": "First name, last name, email, and password are required"
                })
            
            # Validate password confirmation
            if password != confirmPassword:
                return templates.TemplateResponse("register.html", {
                    "request": request,
                    "error": "Passwords do not match"
                })
            
            # Check age requirement based on league
            age_required_leagues = ["npfl", "nnl1", "academy"]
            if league in age_required_leagues and not dob:
                return templates.TemplateResponse("register.html", {
                    "request": request,
                    "error": "Date of birth is required for this league"
                })
            
            # Validate other required fields
            required_fields = {
                "gender": gender,
                "playerNationality": playerNationality,
                "preferredPositionCategory": preferredPositionCategory,
                "preferredPosition": preferredPosition,
                "dominantFoot": dominantFoot,
                "height": height,
                "weight": weight,
                "league": league
            }
            
            missing_fields = [field for field, value in required_fields.items() if not value]
            if missing_fields:
                return templates.TemplateResponse("register.html", {
                    "request": request,
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                })
            
            # Check if email already exists
            if players_collection is not None:
                existing_user = players_collection.find_one({"email": email})
                if existing_user:
                    return templates.TemplateResponse("register.html", {
                        "request": request,
                        "error": "Email already registered"
                    })
            
            # Check for duplicate user by name and email
            if players_collection is not None:
                duplicate_user = players_collection.find_one({
                    "$or": [
                        {"email": email},
                        {"$and": [{"firstName": firstName}, {"lastName": lastName}]}
                    ]
                })
                if duplicate_user:
                    return templates.TemplateResponse("register.html", {
                        "request": request,
                        "error": "User with these credentials already exists"
                    })
            
            # Handle photo upload
            photo_filename = None
            if playerPhoto and playerPhoto.filename:
                try:
                    content = await playerPhoto.read()
                    if len(content) > 200 * 1024:  # 200KB limit
                        return templates.TemplateResponse("register.html", {
                            "request": request,
                            "error": "Photo size must be 200KB or less"
                        })
                    
                    # Create unique filename
                    import time
                    timestamp = int(time.time())
                    file_extension = playerPhoto.filename.split('.')[-1] if '.' in playerPhoto.filename else 'jpg'
                    photo_filename = f"{firstName.lower()}_{lastName.lower()}_{timestamp}.{file_extension}"
                    file_path = uploads_dir / photo_filename
                    
                    with open(file_path, "wb") as buffer:
                        buffer.write(content)
                except Exception as e:
                    print(f"Photo upload error: {e}")
                    return templates.TemplateResponse("register.html", {
                        "request": request,
                        "error": "Failed to upload photo"
                    })
            
            # Hash password
            try:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            except Exception as e:
                print(f"Password hashing error: {e}")
                return templates.TemplateResponse("register.html", {
                    "request": request,
                    "error": "Password processing failed"
                })
            
            # Determine selected club based on league type
            selected_club = None
            if league in ["npfl", "nnl1", "nnl2", "academy"]:
                selected_club = leagueClub
            elif league in ["street", "university"]:
                if generalClub == "not-available":
                    selected_club = customClub
                else:
                    selected_club = generalClub
            
            # Prepare registration data for MongoDB
            registration_data = {
                "userType": userType,
                "firstName": firstName,
                "middleName": middleName or "",
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
                "bio": "",
                "awards": [],
                "achievements": [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Save to database and create dashboard
            try:
                if players_collection is not None:
                    # Remove None values and userType before saving to MongoDB
                    clean_data = {k: v for k, v in registration_data.items() if v is not None}
                    result = players_collection.insert_one(clean_data)
                    print(f"Player registered successfully with ID: {result.inserted_id}")
                    
                    # Create JWT token for immediate login
                    token = create_access_token({"sub": str(result.inserted_id)})
                    response = RedirectResponse(url="/player-dashboard", status_code=303)
                    response.set_cookie("access_token", token, httponly=True, max_age=3600)
                    return response
                else:
                    save_to_json(registration_data)
                    print("Player registered successfully to JSON file")
                    return RedirectResponse(url="/success", status_code=303)
                
            except Exception as e:
                print(f"Database save error: {e}")
                # Try JSON fallback
                try:
                    save_to_json(registration_data)
                    return RedirectResponse(url="/success", status_code=303)
                except Exception as json_error:
                    print(f"JSON fallback error: {json_error}")
                    return templates.TemplateResponse("register.html", {
                        "request": request,
                        "error": "Registration failed. Please try again."
                    })
        else:
            # Other user types not implemented yet
            return templates.TemplateResponse("register.html", {
                "request": request,
                "error": f"{userType.title()} registration coming soon!"
            })
    
    except Exception as e:
        print(f"Registration error: {str(e)}")
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "An unexpected error occurred. Please try again."
        })

@app.post("/validate-player")
async def validate(player: Player):
    """Validate player data using Pydantic model"""
    return {"message": "Player data is valid", "player": player.dict()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
