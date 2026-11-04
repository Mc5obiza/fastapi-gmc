from datetime import datetime
from pydantic import BaseModel

class User(BaseModel):
    id:int
    name: str = "Anonymous"
user = User(id = "123")
print(user.id)