from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

from pydantic.types import conint


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    # owner: UserOut

    class Config:
        orm_mode = True


class PostOut(BaseModel):
    post: Post
    votes: int

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class Vote(BaseModel):
    post_id: int
    vote_direction: conint(le=1)

class   GetAllPosts(BaseModel):
    posts_id: int
    posts_title: str
    posts_content: str
    posts_published: bool
    posts_created_at: datetime
    posts_owner_id: int
    votes: int


#from pydantic import BaseModel, EmailStr, conint
# from datetime import datetime
# from typing import Optional
#
#
# class Vote(BaseModel):
#     post_id: int
#     dir: conint(le=1)
#
#
# class User(BaseModel):
#     email: EmailStr
#     password: str
#
#
# class User_(BaseModel):
#     id: int
#     email: EmailStr
#     created_at: datetime
#
#     class Config:
#         orm_mode = True
#
#
# class UserLogin(BaseModel):
#     email: EmailStr
#     password: str
#
#
# class Post(BaseModel):
#     title: str
#     content: str
#     published: bool = True
#
#
# class Post_(Post):
#     id: int
#     created_at: datetime
#     owner_id: int
#     owner: User_
#     votes: Vote
#
#     class Config:
#         orm_mode = True
#
#
# class PostOut(BaseModel):
#     post: Post_
#     votes: int
#
#     class Config:
#         orm_mode = True
#
#
# class Token(BaseModel):
#     access_token: str
#     token_type: str
#
#
# class TokenData(BaseModel):
#     id: Optional[str] = None
