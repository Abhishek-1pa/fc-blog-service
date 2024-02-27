from pydantic import BaseModel, EmailStr
from typing import List

class BlogCreate(BaseModel):
    author_id:int
    title:str
    content:str
    tags : List[str]
    
class BlogUpdate(BaseModel):
    title:str
    id:int
    content:str
    tags : List[str]
    likes:int
    dislikes:int
    