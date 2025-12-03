from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    username: str
    is_active: bool | None = True
    role: str = "admin"

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)
