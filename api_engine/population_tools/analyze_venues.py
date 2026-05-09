#!/usr/bin/env python3
"""
Script to analyze venues using the analyze_venues_batch function
Accepts venue IDs as command line arguments or analyzes first N venues
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

import google.generativeai as genai
from sqlmodel import Session, create_engine, select
from models import Venue
from venue_utils import analyze_venues_batch


def main():
    """Main execution function"""
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        print("Please set it in your environment:")
        print("PowerShell: $env:GEMINI_API_KEY = 'your_key_here'")
        print("CMD: set GEMINI_API_KEY=your_key_here")
        return
    
    # Configure AI
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Set up database
    db_path = Path(__file__).parent.parent / "plan_engine.db"
    engine = create_engine(f'sqlite:///{db_path.absolute()}')
    session = Session(engine)
    
    try:
        # Parse command line arguments
        if len(sys.argv) > 1:
            # Use provided venue IDs
            try:
                venue_ids = [int(arg) for arg in sys.argv[1:]]
                print(f"🎯 Analyzing specified venue IDs: {venue_ids}")
            except ValueError:
                print("❌ Error: All arguments must be valid venue IDs (integers)")
                return
        else:
            # Analyze all venues without summary
            venue_ids = []  # Empty list will trigger auto-detection in analyze_venues_batch
            print("🎯 Analyzing all venues without summary...")
        
        # Skip verification if using auto-detection (empty list)
        if venue_ids:
            # Verify specific venue IDs exist
            existing_venues = []
            for venue_id in venue_ids:
                venue = session.exec(select(Venue).where(Venue.id == venue_id)).first()
                if venue:
                    existing_venues.append(venue)
                else:
                    print(f"⚠️  Venue with ID {venue_id} not found in database")
            
            if not existing_venues:
                print("❌ No valid venues found to analyze")
                return
            
            final_venue_ids = [v.id for v in existing_venues]
            print(f"📋 Final venue list: {final_venue_ids}")
        else:
            # Use empty list for auto-detection
            final_venue_ids = []
        
        # Analyze venues
        print("\n" + "="*60)
        print("🚀 STARTING VENUE ANALYSIS")
        print("="*60)
        
        results = analyze_venues_batch(final_venue_ids, session, model)
        
        # Mark rejected venues in database
        rejected_venues = []
        for result in results:
            if result.get('rejected', True):
                venue_id = result.get('venue_id')
                venue = session.exec(select(Venue).where(Venue.id == venue_id)).first()
                if venue:
                    venue.summary = "rejected"
                    rejected_venues.append(venue)
                    print(f"   🚫 Marked venue {venue_id} as rejected in database")
        
        if rejected_venues:
            session.commit()
            print(f"   💾 Updated {len(rejected_venues)} venues as rejected in database")
        
        print("\n" + "="*60)
        print(f"📊 ANALYSIS COMPLETE")
        print(f"✅ Processed {len(results)} venues")
        print("="*60)
        
        # Summary
        rejected_count = sum(1 for r in results if r.get('rejected', True))
        accepted_count = len(results) - rejected_count
        
        print(f"\n📈 SUMMARY:")
        print(f"   Accepted: {accepted_count}")
        print(f"   Rejected: {rejected_count}")
        print(f"   Total: {len(results)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()


if __name__ == "__main__":
    # Show usage
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("Usage:")
        print("  python analyze_venues.py                    # Analyze first 5 venues")
        print("  python analyze_venues.py 1 2 3 4 5         # Analyze specific venue IDs")
        print("  python analyze_venues.py --help            # Show this help")
        print("\nPrerequisites:")
        print("  - Set GEMINI_API_KEY environment variable")
        print("  - Have venues in the database")
        sys.exit(0)
    
    main()
