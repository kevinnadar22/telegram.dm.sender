from beanie import Document
from pydantic import Field
from datetime import datetime

class User(Document):
    id: int = Field(alias="_id")
    banned: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "users"

