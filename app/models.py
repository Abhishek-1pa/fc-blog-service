from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, String, TIMESTAMP, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

Base = declarative_base()

class BlogTag(Base):
    __tablename__ = "blogs_tags"

    blog_id = Column(Integer, ForeignKey("blogs.id"),primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"),primary_key=True)
    
class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, unique=True, nullable=False)


class Blog(Base):
    __tablename__ = "blogs"
    id = Column(Integer, primary_key=True, nullable=False)
    author = Column(Integer, primary_key=False, nullable=False)  # Assuming author_id references User table
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    likes = Column(Integer, primary_key=False, nullable=False, default=0)
    dislikes = Column(Integer, primary_key=False, nullable=False, default=0)
    published_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    # Many-to-many relationship with Tag using an associative table
    tags = relationship("Tag", secondary="blogs_tags", backref="blogs", cascade="all, delete")
    comments = relationship("Comment", backref="blogs", cascade="all, delete")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, nullable=False)
    comment = Column(String, nullable=False)
    blog_id = Column(Integer, ForeignKey("blogs.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    username = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    
    def __str__(self):
        return f"User(id={self.id}, username={self.username}, email={self.email})"

    

    