from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
from datetime import datetime
import httpx
import re
import json
import asyncio
from urllib.parse import urlparse

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'neurodivergent_organizer')

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
collection = db.saved_content

# Pydantic models
class ContentItem(BaseModel):
    id: Optional[str] = None
    url: str
    title: Optional[str] = ""
    description: Optional[str] = ""
    thumbnail: Optional[str] = ""
    tags: List[str] = []
    category: Optional[str] = "General"
    date_saved: Optional[datetime] = None
    platform: Optional[str] = "Facebook"

class ContentCreate(BaseModel):
    url: str
    tags: List[str] = []
    category: Optional[str] = "General"

class SearchRequest(BaseModel):
    query: str

async def extract_metadata_from_url(url: str) -> dict:
    """Extract metadata from URL using simple HTTP request and HTML parsing"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Add user agent to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = await client.get(url, headers=headers, follow_redirects=True)
            html = response.text
            
            # Extract title
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else ""
            
            # Extract description from meta tags
            desc_patterns = [
                r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)["\']',
                r'<meta\s+property=["\']og:description["\']\s+content=["\']([^"\']*)["\']',
                r'<meta\s+content=["\']([^"\']*)["\'][^>]*name=["\']description["\']'
            ]
            description = ""
            for pattern in desc_patterns:
                desc_match = re.search(pattern, html, re.IGNORECASE)
                if desc_match:
                    description = desc_match.group(1).strip()
                    break
            
            # Extract thumbnail from meta tags  
            img_patterns = [
                r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']*)["\']',
                r'<meta\s+name=["\']twitter:image["\']\s+content=["\']([^"\']*)["\']',
                r'<meta\s+content=["\']([^"\']*)["\'][^>]*property=["\']og:image["\']'
            ]
            thumbnail = ""
            for pattern in img_patterns:
                img_match = re.search(pattern, html, re.IGNORECASE)
                if img_match:
                    thumbnail = img_match.group(1).strip()
                    break
            
            return {
                "title": title or "Untitled",
                "description": description or "No description available",
                "thumbnail": thumbnail or ""
            }
    except Exception as e:
        print(f"Error extracting metadata: {e}")
        return {
            "title": "Unable to fetch title",
            "description": "Unable to fetch description", 
            "thumbnail": ""
        }

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "Neurodivergent Content Organizer"}

@app.post("/api/content", response_model=ContentItem)
async def save_content(content: ContentCreate):
    """Save a new content item with metadata extraction"""
    
    # Extract metadata from URL
    metadata = await extract_metadata_from_url(content.url)
    
    # Create content item
    content_item = ContentItem(
        id=str(uuid.uuid4()),
        url=content.url,
        title=metadata["title"],
        description=metadata["description"],
        thumbnail=metadata["thumbnail"],
        tags=content.tags,
        category=content.category,
        date_saved=datetime.now(),
        platform="Facebook"  # Default for now
    )
    
    # Save to database
    doc = content_item.dict()
    await collection.insert_one(doc)
    
    return content_item

@app.get("/api/content", response_model=List[ContentItem])
async def get_all_content():
    """Get all saved content"""
    cursor = collection.find({})
    items = []
    async for doc in cursor:
        # Convert MongoDB _id to string and remove it
        doc.pop('_id', None)
        items.append(ContentItem(**doc))
    
    # Sort by date_saved, newest first
    items.sort(key=lambda x: x.date_saved or datetime.min, reverse=True)
    return items

@app.post("/api/search", response_model=List[ContentItem])
async def search_content(search_req: SearchRequest):
    """Search content by title, description, tags, or category"""
    query = search_req.query.lower()
    
    # Create MongoDB text search query
    search_filter = {
        "$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"description": {"$regex": query, "$options": "i"}},
            {"tags": {"$in": [query]}},
            {"category": {"$regex": query, "$options": "i"}}
        ]
    }
    
    cursor = collection.find(search_filter)
    items = []
    async for doc in cursor:
        doc.pop('_id', None)
        items.append(ContentItem(**doc))
    
    # Sort by relevance (could be improved)
    items.sort(key=lambda x: x.date_saved or datetime.min, reverse=True)
    return items

@app.delete("/api/content/{content_id}")
async def delete_content(content_id: str):
    """Delete a content item"""
    result = await collection.delete_one({"id": content_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Content not found")
    return {"message": "Content deleted successfully"}

@app.put("/api/content/{content_id}", response_model=ContentItem)
async def update_content(content_id: str, content: ContentCreate):
    """Update content tags and category"""
    
    update_data = {
        "tags": content.tags,
        "category": content.category
    }
    
    result = await collection.update_one(
        {"id": content_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Return updated item
    doc = await collection.find_one({"id": content_id})
    doc.pop('_id', None)
    return ContentItem(**doc)

@app.get("/api/categories")
async def get_categories():
    """Get all unique categories"""
    pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    categories = []
    async for doc in collection.aggregate(pipeline):
        if doc["_id"]:  # Skip null categories
            categories.append({
                "name": doc["_id"],
                "count": doc["count"]
            })
    
    return categories

@app.get("/api/tags")
async def get_tags():
    """Get all unique tags"""
    pipeline = [
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    tags = []
    async for doc in collection.aggregate(pipeline):
        if doc["_id"]:  # Skip empty tags
            tags.append({
                "name": doc["_id"],
                "count": doc["count"]
            })
    
    return tags

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)