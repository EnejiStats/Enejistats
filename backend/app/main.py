import os import json from pathlib import Path from datetime import datetime, timedelta from typing import Optional, List

import bcrypt from bson.objectid import ObjectId from dotenv import load_dotenv from fastapi import ( FastAPI, Request, Form, File, UploadFile, HTTPException, Response, Cookie ) from fastapi.templating import Jinja2Templates from fastapi.staticfiles import StaticFiles from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse from jose import JWTError, jwt from pymongo import MongoClient from pydantic import BaseModel

Load environment variables

load_dotenv()

app = FastAPI()

Mount static and template directories

app.mount("/static", StaticFiles(directory="static"), name="static") templates = Jinja2Templates(directory="templates")

Ensure uploads directory exists

uploads_dir = Path("static/uploads") uploads_dir.mkdir(parents=True, exist_ok=True)

JWT configuration

SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key") ALGORITHM = "HS256" ACCESS_TOKEN_EXPIRE_MINUTES = 60

MongoDB setup

MONGO_URI = os.getenv("MONGO_URI") players_collection = contact_collection = None if MONGO_URI: try: client = MongoClient(MONGO_URI) db = client["enejistats"] players_collection = db["players"] contact_collection = db["contact_messages"] print("Connected to MongoDB") except Exception as e: print(f"MongoDB connection failed: {e}") else: print("Warning: MONGO_URI not set. Using JSON file storage.")

Pydantic model

class Player(BaseModel): player_id: str first_name: str middle_name: Optional[str] = "" last_name: str dob: str nationality: str preferred_position_category: str preferred_position: str club: str photo_url: str

Helper functions

def create_access_token(data: dict, expires_delta: timedelta = None): to_encode = data.copy() expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)) to_encode.update({"exp": expire}) return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str): try: payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) return payload.get("sub") except JWTError: return None

def save_to_json(data): file_path = Path("registrations.json") registrations = [] if file_path.exists(): with open(file_path, "r") as f: registrations = json.load(f) registrations.append(data) with open(file_path, "w") as f: json.dump(registrations, f, indent=2)

Routes

@app.get("/", response_class=HTMLResponse) async def home(request: Request): for page in ["index.html", "register.html"]: try: return templates.TemplateResponse(page, {"request": request}) except: continue raise HTTPException(status_code=404, detail="Home page not found")

@app.get("/{page}", response_class=HTMLResponse) async def serve_page(request: Request, page: str): pages = { "about": "about.html", "contact": "contact.html", "leaderboard": "leaderboard.html", "browse": "browse.html", "stats-area": "stats-area.html", "stats": "stats_area.html", "player": "player.html", "player-dashboard": "player-dashboard.html", "dashboard": "dashboard.html", "register": "register.html", "login": "login.html" } if page in pages: return templates.TemplateResponse(pages[page], {"request": request}) raise HTTPException(status_code=404, detail="Page not found")

@app.get("/logout") async def logout(): response = RedirectResponse(url="/login") response.delete_cookie("access_token") return response

@app.get("/success", response_class=HTMLResponse) async def registration_success(): return templates.TemplateResponse("success.html", {})

@app.get("/registrations") async def get_registrations(): if players_collection: try: regs = list(players_collection.find({}, {"_id": 0})) return {"registrations": regs, "source": "mongodb"} except Exception as e: print(f"MongoDB query error: {e}") file = Path("registrations.json") if file.exists(): with open(file) as f: return {"registrations": json.load(f), "source": "json"} return {"registrations": [], "source": "none"}

@app.post("/login") async def post_login(response: Response, request: Request, email: str = Form(...), password: str = Form(...)): if not players_collection: return templates.TemplateResponse("login.html", {"request": request, "message": "Database not available."}) user = players_collection.find_one({"email": email}) if not user or not bcrypt.checkpw(password.encode(), user["password"].encode()): return templates.TemplateResponse("login.html", {"request": request, "message": "Invalid email or password."}) token = create_access_token({"sub": str(user["_id"])}) res = RedirectResponse(url="/dashboard") res.set_cookie("access_token", token, httponly=True, max_age=3600) return res

@app.post("/submit-contact") async def submit_contact(request: Request, name: str = Form(...), email: str = Form(...), message: str = Form(...)): data = {"name": name, "email": email, "message": message} if contact_collection: try: contact_collection.insert_one(data) except Exception as e: print(f"Failed to save contact: {e}") return templates.TemplateResponse("contact.html", {"request": request, "success": True})

@app.post("/validate-player") async def validate(player: Player): return {"message": "Player data is valid", "player": player.dict()}

Additional routes such as /register can be modularized for further cleanup

if name == "main": import uvicorn uvicorn.run(app, host="0.0.0.0", port=5000)

