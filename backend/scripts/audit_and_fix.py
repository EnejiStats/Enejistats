from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client.enejistats
players_collection = db.players

def audit_and_fix_players():
    players = players_collection.find()
    for player in players:
        updates = {}

        if "photo_url" not in player:
            updates["photo_url"] = "https://via.placeholder.com/150"

        if "middle_name" not in player:
            updates["middle_name"] = ""

        if "player_id" not in player:
            # Generate unique ID (use a real generator in production)
            updates["player_id"] = str(player["_id"])[-5:]  # Example

        if updates:
            print(f"Fixing player {player.get('_id')}: {updates}")
            players_collection.update_one(
                {"_id": player["_id"]},
                {"$set": updates}
            )

if __name__ == "__main__":
    audit_and_fix_players()
    print("✔️ Player collection audit completed.")
