
import os
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
from dotenv import load_dotenv
import shutil

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up template directory
templates = Jinja2Templates(directory="templates")

# Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI not set in environment.")

client = MongoClient(MONGO_URI)
db = client["enejistats"]
players_collection = db["players"]

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/stats/player", response_class=HTMLResponse)
async def stats_player(request: Request):
    # Optional: redirect to login if not authenticated
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

# GET: Register form
@app.get("/register", response_class=HTMLResponse)
async def get_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# POST: Save player registration
@app.post("/register", response_class=HTMLResponse)
async def post_register(
    request: Request,
    userType: str = Form(...),
    firstName: str = Form(None),
    middleName: str = Form(None),
    lastName: str = Form(None),
    email: str = Form(None),
    password: str = Form(None),
    dob: str = Form(None),
    gender: str = Form(None),
    playerNationality: str = Form(None),
    playerPhoto: UploadFile = File(None),
    dominantFoot: str = Form(None),
    height: str = Form(None),
    weight: str = Form(None),
    league: str = Form(None),
    leagueClub: str = Form(None),
    generalClub: str = Form(None),
    clubAssociation: str = Form(None),
    club: str = Form(None)
):
    if userType != 'player':
        return templates.TemplateResponse("register.html", {
            "request": request, 
            "message": "Only player registration is currently supported."
        })

    # Save photo to /static/uploads/
    photo_filename = None
    if playerPhoto:
        upload_dir = "static/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        photo_filename = f"{firstName.lower()}_{lastName.lower()}.jpg"
        with open(os.path.join(upload_dir, photo_filename), "wb") as buffer:
            shutil.copyfileobj(playerPhoto.file, buffer)

    # Determine selected club
    selected_club = leagueClub or generalClub or club

    # Save to MongoDB
    players_collection.insert_one({
        "firstName": firstName,
        "middleName": middleName,
        "lastName": lastName,
        "email": email,
        "password": password,  # WARNING: hash in production!
        "dob": dob,
        "gender": gender,
        "nationality": playerNationality,
        "photo": photo_filename,
        "dominantFoot": dominantFoot,
        "height": height,
        "weight": weight,
        "league": league,
        "club": selected_club,
        "clubAssociation": clubAssociation
    })

    return templates.TemplateResponse("register.html", {
        "request": request,
        "message": "Registration successful!"
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
