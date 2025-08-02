from typing import Optional
from pydantic import BaseModel


class CreateProfileForm(BaseModel):
    name: str
    avatar_url: Optional[str] = ""


class DeleteProfileForm(BaseModel):
    id: int


class UpdateProfileForm(BaseModel):
    id: int
    name: Optional[str] = ""
    avatar_url: Optional[str] = ""
