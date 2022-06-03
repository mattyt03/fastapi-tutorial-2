from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

# review classes!
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# the field names in the response model must match the field names in the orm model
class UserResponse(BaseModel):
    email: EmailStr
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    created_at: datetime
    owner: UserResponse

    class Config:
        orm_mode = True

class PostResponseWithLikes(BaseModel):
    Post: PostResponse
    # i don't like how this field is separate
    likes: int

class Token(BaseModel):
    access_token: str
    token_type: str

# what are unions?
class TokenPayload(BaseModel):
    user_id: str

# class Like(BaseModel):
#     post_id: int
#     # figure out how to specify either 0 or 1
#     dir: int