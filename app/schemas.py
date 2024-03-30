from pydantic import BaseModel, EmailStr
from typing import List, Dict, Optional
from datetime import datetime
from .import models

class TagCreated(BaseModel):
    id:Optional[int]
    text:str

class CommentCreate(BaseModel):
    blog_id:int
    author_id:int
    comment:str

class CommentCreated(BaseModel):
    id:int
    comment:str
    blog_id:int
    author_id:int
    created_at:datetime

class BlogCreate(BaseModel):
    title:str
    content:Dict
    tags : List[str]
    thumbnail_id: int
    
class BlogCreated(BaseModel):
    id:int
    author:int
    title:str
    content:Dict
    likes:int
    dislikes:int
    published_at:datetime
    tags:List[TagCreated]
    comments:List[CommentCreated]
    thumbnail_id:Optional[int]
    
class BlogUpdate(BaseModel):
    title:str
    id:int
    content:Dict
    tags : List[str]
    thumbnail_id : int
    
