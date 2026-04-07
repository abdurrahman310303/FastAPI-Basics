from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.models import User, Post
from app.schemas.schemas import UserCreate, PostCreate, PostUpdate
from app.utils.auth import get_password_hash
from app.utils.helpers import generate_unique_slug
from typing import Optional, List

# User CRUD operations
def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username."""
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate) -> User:
    """Create new user."""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get list of users."""
    return db.query(User).offset(skip).limit(limit).all()

# Post CRUD operations
def get_post(db: Session, post_id: int) -> Optional[Post]:
    """Get post by ID."""
    return db.query(Post).filter(Post.id == post_id).first()

def get_post_by_slug(db: Session, slug: str) -> Optional[Post]:
    """Get post by slug."""
    return db.query(Post).filter(Post.slug == slug).first()

def get_posts(db: Session, skip: int = 0, limit: int = 100, published_only: bool = False) -> List[Post]:
    """Get list of posts."""
    query = db.query(Post)
    if published_only:
        query = query.filter(Post.is_published == True)
    return query.offset(skip).limit(limit).all()

def get_posts_by_author(db: Session, author_id: int, skip: int = 0, limit: int = 100) -> List[Post]:
    """Get posts by author."""
    return db.query(Post).filter(Post.author_id == author_id).offset(skip).limit(limit).all()

def create_post(db: Session, post: PostCreate, author_id: int) -> Post:
    """Create new post."""
    # Get existing slugs to ensure uniqueness
    existing_posts = db.query(Post).all()
    existing_slugs = [p.slug for p in existing_posts]
    
    slug = generate_unique_slug(post.title, existing_slugs)
    
    db_post = Post(
        title=post.title,
        content=post.content,
        slug=slug,
        is_published=post.is_published,
        author_id=author_id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def update_post(db: Session, post_id: int, post_update: PostUpdate) -> Optional[Post]:
    """Update post."""
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        return None
    
    update_data = post_update.dict(exclude_unset=True)
    
    # If title is being updated, update slug too
    if "title" in update_data:
        existing_posts = db.query(Post).filter(Post.id != post_id).all()
        existing_slugs = [p.slug for p in existing_posts]
        update_data["slug"] = generate_unique_slug(update_data["title"], existing_slugs)
    
    for field, value in update_data.items():
        setattr(db_post, field, value)
    
    db.commit()
    db.refresh(db_post)
    return db_post

def delete_post(db: Session, post_id: int) -> bool:
    """Delete post."""
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        return False
    
    db.delete(db_post)
    db.commit()
    return True

def search_posts(db: Session, query: str, skip: int = 0, limit: int = 100) -> List[Post]:
    """Search posts by title or content."""
    return db.query(Post).filter(
        or_(
            Post.title.ilike(f"%{query}%"),
            Post.content.ilike(f"%{query}%")
        )
    ).offset(skip).limit(limit).all()
