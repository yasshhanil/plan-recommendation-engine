#!/usr/bin/env python3
"""
Update venues table with tagged_venues.json data
Handles rejected venues and merges tags without duplication
"""

import json
import os
from typing import Dict, Any, List, Set
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select
from models import Venue
from sqlmodel import SQLModel

def load_tagged_venues(file_path: str = 'tagged_venues_CP_DELHI.json') -> List[Dict[str, Any]]:
    """Load tagged venues from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: {file_path} not found")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing {file_path}: {e}")
        return []

def merge_tags(existing_tags: List[str], new_tags: List[str]) -> List[str]:
    """Merge existing and new tags without duplication"""
    if not existing_tags:
        return new_tags if new_tags else []
    
    if not new_tags:
        return existing_tags
    
    # Convert to set to remove duplicates, then back to list
    merged_set = set(existing_tags) | set(new_tags)
    return sorted(list(merged_set))  # Sort for consistency

def update_venues_from_tags():
    """Update venues table with tagged data"""
    
    # Load tagged venues
    tagged_venues = load_tagged_venues()
    if not tagged_venues:
        return
    
    print(f"📊 Loaded {len(tagged_venues)} tagged venues")
    
    # Database connection
    database_url = os.getenv('DATABASE_URL', 'sqlite:///./plan_engine.db')
    engine = create_engine(database_url)
    
    # Create tables if they don't exist
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # Get all existing venues
        existing_venues = session.execute(select(Venue)).scalars().all()
        print(f"Found {len(existing_venues)} venues in database")
        venue_dict = {v.id: v for v in existing_venues}
        # print(venue_dict[45].tags)
        print(f"🗄️  Found {len(venue_dict)} venues in database")
        # Statistics
        updated_count = 0
        rejected_count = 0
        not_found_count = 0
        tag_merge_count = 0
        
        for tagged_venue in tagged_venues:
            venue_id = tagged_venue.get('venue_id')
            
            # Skip if venue not found in database
            if venue_id not in venue_dict:
                print(f"⚠️  Venue ID {venue_id} not found in database")
                not_found_count += 1
                continue
            
            venue = venue_dict[venue_id]
            
            # Skip rejected venues
            if tagged_venue.get('rejected', False):
                print(f"🚫 Skipping rejected venue: {venue.name} (ID: {venue_id})")
                rejected_count += 1
                continue
            
            # Get new tags from tagged data
            new_category_tags = tagged_venue.get('category_tags', [])
            new_vibe_tags = tagged_venue.get('vibe_tags', [])
            new_special_tags = tagged_venue.get('special_tags', [])
            
            # Parse existing tags from JSON string
            existing_tags = {}
            if venue.tags:
                try:
                    existing_tags = json.loads(venue.tags)
                except json.JSONDecodeError:
                    existing_tags = {}
            
            # Merge with existing tags
            old_category = existing_tags.get('category_tags', [])
            old_vibe = existing_tags.get('vibe_tags', [])
            old_special = existing_tags.get('special_tags', [])
            
            merged_category = merge_tags(old_category, new_category_tags)
            merged_vibe = merge_tags(old_vibe, new_vibe_tags)
            merged_special = merge_tags(old_special, new_special_tags)
            
            # Check if tags were merged (added new ones)
            tags_merged = (
                len(merged_category) > len(old_category) or
                len(merged_vibe) > len(old_vibe) or
                len(merged_special) > len(old_special)
            )
            
            # Create updated tags structure
            updated_tags = {
                'category_tags': merged_category,
                'vibe_tags': merged_vibe,
                'special_tags': merged_special,
                'price_tags': tagged_venue.get('price_tags', [])
            }
            
            # Update venue data
            venue.summary = tagged_venue.get('summary', venue.summary)
            venue.tags = json.dumps(updated_tags)
            
            # Track if this was a tag merge vs new update
            if tags_merged and (old_category or old_vibe or old_special):
                tag_merge_count += 1
                print(f"🔗 Merged tags for: {venue.name} (ID: {venue_id})")
                print(f"   Category: {old_category} → {merged_category}")
                print(f"   Vibe: {old_vibe} → {merged_vibe}")
                print(f"   Special: {old_special} → {merged_special}")
            else:
                updated_count += 1
                print(f"✅ Updated: {venue.name} (ID: {venue_id})")
                print(f"   Summary: {tagged_venue.get('summary', 'No summary')[:80]}...")
                print(f"   Tags: Category={merged_category}, Vibe={merged_vibe}, Special={merged_special}")
        
        # Commit changes
        try:
            session.commit()
            print(f"\n🎉 Update Complete!")
            print(f"✅ Updated venues: {updated_count}")
            print(f"🔗 Tag merges: {tag_merge_count}")
            print(f"🚫 Rejected venues skipped: {rejected_count}")
            print(f"⚠️  Venues not found: {not_found_count}")
            print(f"💾 Changes committed to database")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error committing changes: {e}")

def show_tag_statistics():
    """Show statistics about tagged venues"""
    
    tagged_venues = load_tagged_venues()
    if not tagged_venues:
        return
    
    print(f"\n📊 Tag Statistics")
    print("=" * 50)
    
    accepted = [v for v in tagged_venues if not v.get('rejected', False)]
    rejected = [v for v in tagged_venues if v.get('rejected', False)]
    
    print(f"Total venues: {len(tagged_venues)}")
    print(f"✅ Accepted: {len(accepted)}")
    print(f"❌ Rejected: {len(rejected)}")
    
    if accepted:
        print(f"\n📋 Accepted Venue Breakdown:")
        category_counts = {}
        vibe_counts = {}
        special_counts = {}
        
        for venue in accepted:
            for tag in venue.get('category_tags', []):
                category_counts[tag] = category_counts.get(tag, 0) + 1
            for tag in venue.get('vibe_tags', []):
                vibe_counts[tag] = vibe_counts.get(tag, 0) + 1
            for tag in venue.get('special_tags', []):
                special_counts[tag] = special_counts.get(tag, 0) + 1
        
        print(f"\n🏷️  Category Tags:")
        for tag, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {tag}: {count}")
        
        print(f"\n🎭 Vibe Tags:")
        for tag, count in sorted(vibe_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {tag}: {count}")
        
        print(f"\n⭐ Special Tags:")
        for tag, count in sorted(special_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {tag}: {count}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        show_tag_statistics()
    else:
        print("🔄 Updating venues table with tagged data...")
        print("=" * 50)
        update_venues_from_tags()
        
        print(f"\n" + "=" * 50)
        show_tag_statistics()
