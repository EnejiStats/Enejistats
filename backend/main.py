backend_main.py (FastAPI backend for Enejistats)

from fastapi import FastAPI, HTTPException, Depends from fastapi.middleware.cors import CORSMiddleware from pydantic import BaseModel, EmailStr from typing import List, Optional from datetime import date, datetime from bson import ObjectId from pymongo import MongoClient import os

Connect to MongoDB

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017") client = MongoClient(MONGO_URL) db = client.enejistats

app = FastAPI()

Allow frontend access

app.add_middleware( CORSMiddleware, allow_origins=[""], allow_credentials=True, allow_methods=[""], allow_headers=["*"], )

----- Models -----

class UserBase(BaseModel): full_name: str email: EmailStr password: str

class PlayerProfile(BaseModel): full_name: str dob: date nationality: str position: str foot: str height: float club: Optional[str] = None bio: Optional[str] = "" awards: Optional[str] = ""

class ClubProfile(BaseModel): name: str country: str bio: Optional[str] = "" achievements: Optional[str] = ""

class ScoutProfile(BaseModel): full_name: str region: str contact: Optional[str] = None role: str

class MatchStats(BaseModel): player_id: str match_id: str goals: int shots_on: int shots_off: int short_pass_success: int short_pass_fail: int long_pass_success: int long_pass_fail: int cross_success: int cross_fail: int interceptions: int tackles: int clearances: int saves: int yellow: int red: int fouls: int offside: int minutes_played: int

class ClubMatchStats(BaseModel): club_id: str match_id: str goals: int shots_on: int shots_off: int possession: float corners: int fouls_won: int offside: int yellow: int red: int pass_stats: dict defence_stats: dict

class LeaderboardEntry(BaseModel): player_id: str name: str position: str photo_url: str composite_score: float week: int

----- Routes -----

@app.post("/register/player") def register_player(player: PlayerProfile): result = db.players.insert_one(player.dict()) return {"player_id": str(result.inserted_id)}

@app.post("/register/club") def register_club(club: ClubProfile): result = db.clubs.insert_one(club.dict()) return {"club_id": str(result.inserted_id)}

@app.post("/register/scout") def register_scout(scout: ScoutProfile): result = db.scouts.insert_one(scout.dict()) return {"scout_id": str(result.inserted_id)}

@app.post("/stats/player") def submit_player_stats(stats: MatchStats): result = db.player_stats.insert_one(stats.dict()) return {"status": "success"}

@app.post("/stats/club") def submit_club_stats(stats: ClubMatchStats): result = db.club_stats.insert_one(stats.dict()) return {"status": "success"}

@app.get("/player/{player_id}") def get_player(player_id: str): player = db.players.find_one({"_id": ObjectId(player_id)}) if not player: raise HTTPException(status_code=404, detail="Player not found") player["_id"] = str(player["_id"]) return player

@app.get("/club/{club_id}") def get_club(club_id: str): club = db.clubs.find_one({"_id": ObjectId(club_id)}) if not club: raise HTTPException(status_code=404, detail="Club not found") club["_id"] = str(club["_id"]) return club

@app.get("/scout/{scout_id}") def get_scout(scout_id: str): scout = db.scouts.find_one({"_id": ObjectId(scout_id)}) if not scout: raise HTTPException(status_code=404, detail="Scout not found") scout["_id"] = str(scout["_id"]) return scout

@app.get("/player/{player_id}/stats") def get_player_stats(player_id: str): stats = list(db.player_stats.find({"player_id": player_id})) for s in stats: s["_id"] = str(s["_id"]) return stats

@app.get("/club/{club_id}/stats") def get_club_stats(club_id: str): stats = list(db.club_stats.find({"club_id": club_id})) for s in stats: s["_id"] = str(s["_id"]) return stats

@app.get("/leaderboard/{week}") def get_leaderboard(week: int): entries = list(db.leaderboard.find({"week": week}).sort("composite_score", -1)) for e in entries: e["_id"] = str(e["_id"]) return entries

@app.post("/leaderboard/update") def update_leaderboard(entry: LeaderboardEntry): db.leaderboard.insert_one(entry.dict()) return {"status": "entry added"}

@app.get("/browse/players") def browse_players(): players = list(db.players.find()) for p in players: p["_id"] = str(p["_id"]) return players

@app.get("/browse/clubs") def browse_clubs(): clubs = list(db.clubs.find()) for c in clubs: c["_id"] = str(c["_id"]) return clubs
