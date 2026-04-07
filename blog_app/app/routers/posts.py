from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.database.crud import (
    get_posts, get_post, get_post_by_slug, create_post, 
    update_post, delete_post, get_posts_by_author, search_posts
)
from app.schemas.schemas import PostCreate, PostUpdate, PostResponse, PostSummary
from app.core.dependencies import get_current_active_user
from app.models.models import User

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.get("/", response_model=List[PostSummary])
def read_posts(
    skip: int = 0,
    limit: int = 100,
    published_only: bool = Query(True, description="Show only published posts"),
    db: Session = Depends(get_db)
):
    """Get list of posts."""
    posts = get_posts(db, skip=skip, limit=limit, published_only=published_only)
    return posts

@router.get("/search", response_model=List[PostSummary])
def search_posts_endpoint(
    q: str = Query(..., description="Search query"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Search posts by title or content."""
    posts = search_posts(db, query=q, skip=skip, limit=limit)
    return posts

@router.get("/my-posts", response_model=List[PostSummary])
def read_my_posts(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's posts."""
    posts = get_posts_by_author(db, author_id=current_user.id, skip=skip, limit=limit)
    return posts

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_new_post(
    post: PostCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new post."""
    return create_post(db=db, post=post, author_id=current_user.id)

@router.get("/{post_id}", response_model=PostResponse)
def read_post(post_id: int, db: Session = Depends(get_db)):
    """Get post by ID."""
    post = get_post(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.get("/slug/{slug}", response_model=PostResponse)
def read_post_by_slug(slug: str, db: Session = Depends(get_db)):
    """Get post by slug."""
    post = get_post_by_slug(db, slug=slug)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.put("/{post_id}", response_model=PostResponse)
def update_post_endpoint(
    post_id: int,
    post_update: PostUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a post."""
    # Check if post exists and user owns it
    existing_post = get_post(db, post_id=post_id)
    if not existing_post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if existing_post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    updated_post = update_post(db, post_id=post_id, post_update=post_update)
    return updated_post

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post_endpoint(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a post."""
    # Check if post exists and user owns it
    existing_post = get_post(db, post_id=post_id)
    if not existing_post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if existing_post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    success = delete_post(db, post_id=post_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete post")
