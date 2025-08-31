import sys
import json
from pathlib import Path
import logging
from datetime import datetime
from typing import Dict, Any, List

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent.parent))
from app.db.connection import get_db
from app.repository.store import load_repository

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def migrate_ceos_to_db():
    """Migrate CEO data from repository.json to SQLite database"""
    # Load the repository
    repo = load_repository()
    
    # Get the database connection
    db = get_db()
    
    # Initialize the database schema if needed
    db.init_schema()
    
    # Begin transaction
    try:
        # Process CEOs
        for ceo_name in repo.list_ceo_names():
            ceo_data = repo.get_ceo(ceo_name)
            
            # Skip if no data
            if not ceo_data:
                continue
            
            # Extract company and industry
            company = ceo_data.get("company", "")
            industry = ceo_data.get("industry", "")
            
            # Insert CEO
            cursor = db.execute(
                "INSERT OR IGNORE INTO ceos (name, company, industry) VALUES (?, ?, ?)",
                (ceo_name, company, industry)
            )
            
            # Get CEO ID
            if cursor.lastrowid:
                ceo_id = cursor.lastrowid
            else:
                # CEO already exists, get the ID
                result = db.fetchone("SELECT id FROM ceos WHERE name = ?", (ceo_name,))
                ceo_id = result["id"]
            
            # Create a default profile version for now (can be enhanced later)
            cursor = db.execute(
                "INSERT OR IGNORE INTO ceo_profile_versions (ceo_id, version_label, valid_from) VALUES (?, ?, ?)",
                (ceo_id, "Default", datetime.now().strftime("%Y-%m-%d"))
            )
            
            # Get version ID
            if cursor.lastrowid:
                version_id = cursor.lastrowid
            else:
                # Version already exists, get the ID
                result = db.fetchone(
                    "SELECT id FROM ceo_profile_versions WHERE ceo_id = ? AND version_label = ?",
                    (ceo_id, "Default")
                )
                version_id = result["id"]
            
            # Process profile facts
            pillars = ["strategic_philosophy", "leadership_style", "operational_cadence", "personal_ethos"]
            for pillar in pillars:
                if pillar in ceo_data:
                    for field, value in ceo_data[pillar].items():
                        if value:
                            db.execute(
                                """
                                INSERT OR REPLACE INTO profile_facts 
                                (profile_version_id, pillar, field, value) 
                                VALUES (?, ?, ?, ?)
                                """,
                                (version_id, pillar, field, value)
                            )
        
        # Process situations
        for situation in repo._situations:
            ceo_name = situation.get("ceo")
            if not ceo_name:
                continue
                
            # Get CEO ID
            result = db.fetchone("SELECT id FROM ceos WHERE name = ?", (ceo_name,))
            if not result:
                continue
            ceo_id = result["id"]
            
            # Insert situation
            cursor = db.execute(
                """
                INSERT INTO situations 
                (ceo_id, title, situation, approach, outcome) 
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    ceo_id,
                    situation.get("title", "Untitled"),
                    situation.get("situation", ""),
                    situation.get("response", ""),
                    situation.get("outcome", "")
                )
            )
            
            situation_id = cursor.lastrowid
            
            # Process tags
            for tag in situation.get("tags", []):
                # Insert tag if it doesn't exist
                category = None
                if ":" in tag:
                    category, _ = tag.split(":", 1)
                
                db.execute(
                    "INSERT OR IGNORE INTO tags (name, category) VALUES (?, ?)",
                    (tag, category)
                )
                
                # Get tag ID
                result = db.fetchone("SELECT id FROM tags WHERE name = ?", (tag,))
                if result:
                    tag_id = result["id"]
                    
                    # Link tag to situation
                    db.execute(
                        "INSERT OR IGNORE INTO situation_tags (situation_id, tag_id) VALUES (?, ?)",
                        (situation_id, tag_id)
                    )
        
        # Commit the transaction
        db.commit()
        logger.info("Migration completed successfully")
        
    except Exception as e:
        # Rollback on error
        db.rollback()
        logger.error(f"Error during migration: {e}")
        raise

if __name__ == "__main__":
    migrate_ceos_to_db()
