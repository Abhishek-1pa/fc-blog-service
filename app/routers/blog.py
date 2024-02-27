from fastapi import APIRouter, Depends, status, HTTPException, Depends
from sqlalchemy.orm import Session
from .. import database, models, schemas
from functools import wraps
from ..authentication.authenticator import auth_required
from typing import List

router = APIRouter(
    tags=['blogs'],
    prefix="/blogs"
)

@router.post("/create")
async def create_blog(
    blog: schemas.BlogCreate,
    current_user: models.User = Depends(auth_required),
    db: Session = Depends(database.get_db)
):
    tags = blog.tags
    tag_ids = []
    try:
        for tag_name in tags:
            tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
            if tag:
                tag_id = tag.id
            else:
                new_tag = models.Tag(name=tag_name)
                db.add(new_tag)
                db.flush()  # Flush the changes to generate IDs but don't commit yet
                tag_id = new_tag.id
            tag_ids.append(tag_id)

        # Create the blog
        new_blog = models.Blog(
            author=current_user.id,
            title=blog.title,
            content=blog.content
        )
        db.add(new_blog)
        db.flush()  # Flush the changes to generate the blog ID but don't commit yet
        db.commit()
        # Associate tags with the blog
        for tag_id in tag_ids:
            db.add(models.BlogTag(blog_id=new_blog.id
                                  , tag_id = tag_id))
            # db.execute(models.BlogTag.insert().values(blog_id=new_blog.id, tag_id=tag_id))

        db.commit()  # Commit all the changes
        db.refresh(new_blog)
        return new_blog
    except:
        db.rollback()  # Rollback the transaction if any error occurs
        raise

@router.delete("/delete/{blog_id}")
async def delete_blog(
    blog_id:int,
    current_user : models.Blog = Depends(auth_required),
    db: Session = Depends(database.get_db)
):
    blog :models.Blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
    if current_user.id !=blog.author:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to delete this blog")
    try:
        db.delete(blog)
        db.commit()
        return {"message": "Blog deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occured while deleting the blog")
    
@router.put("/update")
async def update_blog(
    blog: schemas.BlogUpdate,
    current_user: models.User = Depends(auth_required),
    db: Session = Depends(database.get_db)
):
    existing_blog:models.Blog = db.query(models.Blog).filter(models.Blog.id == blog.id).first()
    if not existing_blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")

    if current_user.id != existing_blog.author:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to update this blog")

    try:
        # Update the blog fields if provided in the request
        if blog.title:
            existing_blog.title = blog.title
        if blog.content:
            existing_blog.content = blog.content
        if blog.likes:
            existing_blog.likes = blog.likes
        if blog.dislikes:
            existing_blog.dislikes = blog.dislikes
            
            
        existing_blog.tags.clear()
        # Update tags associated with the blog
        if blog.tags:
            tag_ids = []
  
            for tag_name in blog.tags:
                tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
                if not tag:
                    tag = models.Tag(name = tag_name)
                    db.add(tag)
                existing_blog.tags.append(tag)
    
        db.commit()
        db.refresh(existing_blog)
        return existing_blog
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while updating the blog")

@router.get("/fetch_all")
async def fetch_all(
    db:Session = Depends(database.get_db)
):
    blogs:List[models.Blog] = db.query(models.Blog).all()
    return blogs

@router.get("/tags/{blog_id}")
async def get_tags(
    blog_id:int,
    db:Session = Depends(database.get_db)
):
    tags:List[models.Tag] = db.query(models.Tag).join(models.BlogTag, models.BlogTag.tag_id == models.Tag.id).filter(models.BlogTag.blog_id == blog_id).all()
    return tags

@router.get("/{blog_id}")
async def fetch_blog(
    blog_id: int,
    db:Session = Depends(database.get_db)
    ):
    blog:models.Blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
    
    return blog

