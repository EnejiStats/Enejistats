from pydantic import BaseModel, Field
from typing import Optional

class Player(BaseModel):
    player_id: str
    first_name: str
    middle_name: Optional[str] = ""
    last_name: str
    dob: str  # YYYY-MM-DD
    nationality: str
    preferred_position_category: str
    preferred_position: str
    club: str
    photo_url: str
