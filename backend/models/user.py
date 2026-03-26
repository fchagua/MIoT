from sqlmodel import SQLModel, Field
from datetime import datetime, timezone

class User(SQLModel, table=True):
    id: int | None = Field(default= None, primary_key=True)
    email: str 
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
