import re
from typing import Optional

def create_slug(title: str) -> str:
    """Create a URL-friendly slug from title."""
    # Remove special characters and create slug
    slug = re.sub(r'[^\w\s-]', '', title).strip().lower()
    slug = re.sub(r'[\s_-]+', '-', slug)
    return slug

def generate_unique_slug(title: str, existing_slugs: list = None) -> str:
    """Generate a unique slug."""
    base_slug = create_slug(title)
    if not existing_slugs or base_slug not in existing_slugs:
        return base_slug
    
    counter = 1
    while f"{base_slug}-{counter}" in existing_slugs:
        counter += 1
    
    return f"{base_slug}-{counter}"
