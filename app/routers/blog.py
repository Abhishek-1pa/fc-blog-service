from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File, Response, Form, Body
from sqlalchemy.orm import Session, joinedload
from .. import database, models, schemas
from functools import wraps
from ..authentication.authenticator import auth_required
from typing import List, Annotated
from PIL import Image
import json
import io
import ast
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
    # print(blog)
    tag_ids = []
    try:
        for tag_name in tags:
            tag = db.query(models.Tag).filter(models.Tag.text == tag_name).first()
            if tag:
                tag_id = tag.id
            else:
                print(tag_name)
                new_tag = models.Tag(text=tag_name)
                db.add(new_tag)
                db.flush()  # Flush the changes to generate IDs but don't commit yet
                tag_id = new_tag.id
            tag_ids.append(tag_id)
        print(tags)
        # Create the blog
        new_blog = models.Blog(
            author=current_user.id,
            title=blog.title,
            content=blog.content,
            thumbnail_id = blog.thumbnail_id
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
    print(blog)
    try:
        existing_blog:models.Blog = db.query(models.Blog).filter(models.Blog.id == blog.id).first()
        if not existing_blog:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")

        if current_user.id != existing_blog.author:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to update this blog")


        # Update the blog fields if provided in the request
        if blog.title:
            existing_blog.title = blog.title
        if blog.content:
            existing_blog.content = blog.content
        if blog.thumbnail_id:
            existing_blog.thumbnail_id = blog.thumbnail_id
            
        existing_blog.tags.clear()
        # Update tags associated with the blog
        if blog.tags:
            tag_ids = []
            print(blog.tags)
            for tag_name in blog.tags:
                print(tag_name)
                tag = db.query(models.Tag).filter(models.Tag.text == tag_name).first()
                print(tag_name)
                if not tag:
                    tag = models.Tag(text = tag_name)
                    db.add(tag)
                existing_blog.tags.append(tag)
    
        db.commit()
        db.refresh(existing_blog)
        return existing_blog
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while updating the blog")

@router.get("/fetch_all", response_model=List[schemas.BlogCreated])
async def fetch_all(
    db:Session = Depends(database.get_db)
):
    blogs_with_tags = db.query(models.Blog).options(joinedload(models.Blog.tags)).all()
    return blogs_with_tags

@router.get("/tags/{blog_id}")
async def get_tags(
    blog_id:int,
    db:Session = Depends(database.get_db)
):
    tags:List[models.Tag] = db.query(models.Tag).join(models.BlogTag, models.BlogTag.tag_id == models.Tag.id).filter(models.BlogTag.blog_id == blog_id).all()
    return tags

@router.get("/{blog_id}", response_model=schemas.BlogCreated)
async def fetch_blog(
    blog_id: int,
    db:Session = Depends(database.get_db)
    ):
    blog:schemas.BlogCreated = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
    return blog


@router.get("/image/{id}")
async def fetchImage(id:int,db:Session = Depends(database.get_db)):
    image :models.Image  = db.query(models.Image).filter(models.Image.id == id).first()
    if image is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Image not found")
    image_bytes_io = io.BytesIO(image.image_data)
    pil_image = Image.open(image_bytes_io)
    image_format = pil_image.format.lower()
    image_bytes_io.seek(0)
    image_bytes = image_bytes_io.getvalue()
    
    return Response(content=image_bytes, media_type=f"image/{image_format}")
    
@router.get("/thumbnail/{id}")
async def fetchThumbnail(id:int , db: Session = Depends(database.get_db)):
    thumbnail : models.Thumbnail = db.query(models.Thumbnail).filter(models.Thumbnail.id == id).first()
    if thumbnail is None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Thumbnail not found")
    image_bytes_io = io.BytesIO(thumbnail.image_data)
    pil_image = Image.open(image_bytes_io)
    image_format = pil_image.format.lower()
    image_bytes_io.seek(0)
    image_bytes = image_bytes_io.getvalue()
    return Response(content=image_bytes, media_type=f'image/{image_format}')

@router.post("/uploadFile")
async def uploadFile(
    filename: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth_required)
):
    try:
        # Print incoming request information (for debugging purposes)
        print(f"Received file: {filename.filename}")
        print(f"Content type: {filename.content_type}")

        # ... rest of your code ...

        x = await save_to_image(filename, db, current_user)
        return {"img_id": x}
    except HTTPException as e:
        # Catch specific HTTPException (e.g., 422) raised during validation
        print(f"Validation Error: {e}")
        # Optionally re-raise the exception for the client to handle
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")
    

@router.put("/like/{blog_id}")
async def likeBlog(
    blog_id:int,
    current_user: models.User = Depends(auth_required),
    db:Session = Depends(database.get_db)
):
    user_action : models.UserActions = db.query(models.UserActions).filter(models.UserActions.blog_id == blog_id, models.UserActions.user_id == current_user.id).first()
    if user_action:
        if user_action.action == 1:#already liked
            raise HTTPException(status_code=400, detail="You have already liked the blog")
        else:#user previously disliked the blog
            user_action.action = 1
            blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
            blog.likes += 1
            blog.dislikes -= 1
            db.commit()
            db.refresh(blog)
            return blog
    else:
        new_action = models.UserActions(
            user_id = current_user.id,
            blog_id = blog_id,
            action = 1    
        )
        db.add(new_action)
        blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
        blog.likes += 1
        db.commit()
        db.refresh(blog)
        return blog
    

@router.put("/dislike/{blog_id}")
async def dislikeBlog(
    blog_id:int,
    current_user: models.User = Depends(auth_required),
    db:Session = Depends(database.get_db)
):
    user_action : models.UserActions = db.query(models.UserActions).filter(models.UserActions.blog_id == blog_id, models.UserActions.user_id == current_user.id).first()
    if user_action:
        if user_action.action ==1:#user previously liked
            user_action.action = -1
            blog :models.Blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
            blog.likes = blog.likes-1
            blog.dislikes = blog.dislikes+1
            db.commit()
            db.refresh(blog)
            return blog
        else:
            raise HTTPException(status_code=400, detail="You have already disliked the blog")
    else:
        new_action = models.UserActions(
            user_id = current_user.id,
            blog_id = blog_id,
            action = -1
        )
        db.add(new_action)
        blog: models.Blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
        blog.dislikes = blog.dislikes+1
        db.commit()
        db.refresh(blog)
        return blog
     
@router.post("/add_comment") 
async def addComment(
    payload: schemas.CommentCreate,
    db: Session = Depends(database.get_db)
):
    print(payload)
    comment : models.Comment = models.Comment(**payload.dict())
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment
    
async def save_to_image(file: UploadFile, db: Session, user: models.User):

    if file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(status_code=400, detail="Only JPEG and PNG images allowed")
    
    try:
        image_data = await file.read()
        img = Image.open(io.BytesIO(image_data))
        optimezed_data = io.BytesIO()
        
        img.save(optimezed_data, format=img.format, quality=80)
        image_data = optimezed_data.getvalue()
        
        new_image = models.Image(
            filename=file.filename,
            format=file.content_type.split("/")[1],
            image_data=image_data,
            size=len(image_data),
            poster_id=user.id
        )
        
        db.add(new_image)
        db.commit()
        db.refresh(new_image)
        
        return new_image.id
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")
        
        
async def save_to_thumbnail(file: UploadFile, db: Session, user: models.User):

    if file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(status_code=400, detail="Only JPEG and PNG images allowed")
    
    try:
        image_data = await file.read()
        img = Image.open(io.BytesIO(image_data))
        optimezed_data = io.BytesIO()
        
        img.save(optimezed_data, format=img.format, quality=80)
        image_data = optimezed_data.getvalue()
        
        new_image = models.Thumbnail(
            filename=file.filename,
            format=file.content_type.split("/")[1],
            image_data=image_data,
            size=len(image_data),
            poster_id=user.id
        )
        
        db.add(new_image)
        db.commit()
        db.refresh(new_image)
        
        return new_image.id
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")
        
        
        
           
    