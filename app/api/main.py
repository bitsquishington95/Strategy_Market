# app/api/main.py
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sys
import json
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import models and engine
from app.models.temporal import CEOProfileVersionOut, CEOCardOut, SituationOut
from app.engine.embeddings import get_embedding_engine

# Import database connection if available
try:
    from app.db.connection import get_db_conn
    DB_AVAILABLE = True
except ImportError:
    print("Database connection not available")
    DB_AVAILABLE = False

app = FastAPI(title="Successful CEOs API", version="0.1.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request/Response models ---
class ListCEOsResponse(BaseModel):
    items: List[CEOCardOut]

class CompareRequest(BaseModel):
    ids: List[int]

class QueryRequest(BaseModel):
    query: str
    top_k: int = 10

# --- Helper to run DB query ---
def fetch_rows(query: str, params: tuple = ()):
    """Execute a SQL query and return the results as dictionaries"""
    if not DB_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")
    
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(query, params)
    
    # Convert rows to dictionaries
    columns = [col[0] for col in cur.description]
    rows = [dict(zip(columns, row)) for row in cur.fetchall()]
    
    return rows

# --- API Routes ---
@app.get("/api/ceos", response_model=ListCEOsResponse)
def list_ceos(
    query: Optional[str] = Query(None, description="Free text search query"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    era: Optional[str] = Query(None, description="Filter by era"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    limit: int = Query(100, description="Maximum number of results")
):
    """
    List CEOs with optional filtering.
    """
    if not DB_AVAILABLE:
        # Fallback to dummy data if database is not available
        return {"items": [
            {"id": 1, "name": "Steve Jobs", "company": "Apple", "industry": "Technology", "eras": ["1976-1985", "1997-2011"]},
            {"id": 2, "name": "Jeff Bezos", "company": "Amazon", "industry": "Retail", "eras": ["1994-2021"]},
            {"id": 3, "name": "Satya Nadella", "company": "Microsoft", "industry": "Technology", "eras": ["2014-present"]}
        ]}
    
    # Build SQL query with filters
    sql = """
    SELECT c.id, c.name, c.company, c.industry, v.version_label, v.valid_from, v.valid_to 
    FROM ceos c 
    LEFT JOIN ceo_profile_versions v ON v.ceo_id = c.id
    """
    
    filters = []
    params = []
    
    if industry:
        filters.append("c.industry = ?")
        params.append(industry)
    
    if era:
        filters.append("v.era_tags LIKE ?")
        params.append(f"%{era}%")
    
    if query:
        filters.append("(c.name LIKE ? OR c.company LIKE ?)")
        params.extend([f"%{query}%", f"%{query}%"])
    
    if tags:
        tag_list = tags.split(",")
        for tag in tag_list:
            filters.append("v.era_tags LIKE ?")
            params.append(f"%{tag.strip()}%")
    
    if filters:
        sql += " WHERE " + " AND ".join(filters)
    
    sql += " GROUP BY c.id LIMIT ?"
    params.append(limit)
    
    # Execute query
    rows = fetch_rows(sql, tuple(params))
    
    # Format response
    items = []
    for row in rows:
        items.append(CEOCardOut(
            id=row["id"],
            name=row["name"],
            company=row.get("company", ""),
            industry=row.get("industry", ""),
            eras=[row["version_label"]] if row.get("version_label") else []
        ))
    
    return {"items": items}

@app.get("/api/ceos/{ceo_id}", response_model=CEOProfileVersionOut)
def get_ceo(ceo_id: int):
    """
    Get detailed information about a specific CEO, including all profile versions.
    """
    if not DB_AVAILABLE:
        # Fallback to dummy data
        if ceo_id == 1:  # Steve Jobs
            return {
                "id": 1,
                "name": "Steve Jobs",
                "company": "Apple",
                "industry": "Technology",
                "versions": [
                    {
                        "id": 1,
                        "version_label": "Apple I (1976-1985)",
                        "valid_from": "1976-04-01",
                        "valid_to": "1985-09-16",
                        "era_tags": ["early_apple", "personal_computing"],
                        "facts": [
                            {"pillar": "strategic_philosophy", "field": "core_ideology", "value": "Build insanely great, integrated products that delight users."},
                            {"pillar": "leadership_style", "field": "hiring_philosophy", "value": "A-players only; passion and intelligence over credentials"}
                        ]
                    },
                    {
                        "id": 2,
                        "version_label": "Return to Apple (1997-2011)",
                        "valid_from": "1997-07-09",
                        "valid_to": "2011-08-24",
                        "era_tags": ["apple_renaissance", "digital_hub"],
                        "facts": [
                            {"pillar": "strategic_philosophy", "field": "core_ideology", "value": "Build insanely great, integrated products that delight users."},
                            {"pillar": "leadership_style", "field": "hiring_philosophy", "value": "A-players only; passion and intelligence over credentials"}
                        ]
                    }
                ]
            }
        raise HTTPException(status_code=404, detail="CEO not found")
    
    # Get base CEO information
    ceo_rows = fetch_rows("SELECT * FROM ceos WHERE id = ?", (ceo_id,))
    if not ceo_rows:
        raise HTTPException(status_code=404, detail="CEO not found")
    
    ceo = ceo_rows[0]
    
    # Get versions
    versions = fetch_rows(
        "SELECT * FROM ceo_profile_versions WHERE ceo_id = ? ORDER BY valid_from", 
        (ceo_id,)
    )
    
    # Process each version
    for version in versions:
        # Parse era_tags JSON if present
        if version.get("era_tags"):
            try:
                version["era_tags"] = json.loads(version["era_tags"])
            except json.JSONDecodeError:
                version["era_tags"] = version["era_tags"].split(",")
        else:
            version["era_tags"] = []
        
        # Get facts for this version
        facts = fetch_rows(
            "SELECT pillar, field, value, confidence, citations FROM profile_facts WHERE profile_version_id = ?", 
            (version["id"],)
        )
        
        # Process facts
        for fact in facts:
            # Parse citations JSON if present
            if fact.get("citations"):
                try:
                    fact["citations"] = json.loads(fact["citations"])
                except json.JSONDecodeError:
                    fact["citations"] = []
            else:
                fact["citations"] = []
        
        version["facts"] = facts
    
    return CEOProfileVersionOut(
        id=ceo["id"],
        name=ceo["name"],
        company=ceo.get("company", ""),
        industry=ceo.get("industry", ""),
        versions=versions
    )

@app.get("/api/situations", response_model=List[SituationOut])
def list_situations(
    ceo_id: Optional[int] = Query(None, description="Filter by CEO ID"),
    tag: Optional[str] = Query(None, description="Filter by situation tag"),
    limit: int = Query(200, description="Maximum number of results")
):
    """
    List situations with optional filtering.
    """
    if not DB_AVAILABLE:
        # Fallback to dummy data
        return [
            {
                "id": 1,
                "ceo_id": 1,
                "title": "iPhone 4 Antenna Issue",
                "tags": ["situation:product_launch_crisis", "situation:pr_crisis"],
                "situation": "Users reported signal loss when holding the phone a certain way",
                "approach": "Called press conference, demonstrated issue affects all phones, offered free cases",
                "principles": ["principle:control_narrative", "principle:minimal_concession"],
                "outcome": "Neutralized PR crisis while avoiding recall",
                "occurred_on": "2010-07-16",
                "applies_version_id": 2,
                "confidence": 1.0,
                "citations": ["https://example.com/citation1"]
            }
        ]
    
    # Build SQL query with filters
    q = "SELECT * FROM situations"
    filters = []
    params = []
    
    if ceo_id:
        filters.append("ceo_id = ?")
        params.append(ceo_id)
    
    if tag:
        filters.append("tags LIKE ?")
        params.append(f"%{tag}%")
    
    if filters:
        q += " WHERE " + " AND ".join(filters)
    
    q += " ORDER BY occurred_on DESC LIMIT ?"
    params.append(limit)
    
    # Execute query
    rows = fetch_rows(q, tuple(params))
    
    # Process results
    situations = []
    for row in rows:
        # Parse JSON fields
        tags = []
        principles = []
        citations = []
        
        if row.get("tags"):
            try:
                tags = json.loads(row["tags"])
            except json.JSONDecodeError:
                tags = row["tags"].split(",")
        
        if row.get("principles"):
            try:
                principles = json.loads(row["principles"])
            except json.JSONDecodeError:
                principles = row["principles"].split(",")
        
        if row.get("citations"):
            try:
                citations = json.loads(row["citations"])
            except json.JSONDecodeError:
                citations = []
        
        situations.append(SituationOut(
            id=row["id"],
            ceo_id=row["ceo_id"],
            title=row.get("title", ""),
            tags=tags,
            situation=row.get("situation", ""),
            approach=row.get("approach", ""),
            principles=principles,
            outcome=row.get("outcome"),
            occurred_on=row.get("occurred_on"),
            applies_version_id=row.get("applies_version_id"),
            confidence=row.get("confidence", 1.0),
            citations=citations
        ))
    
    return situations

@app.post("/api/compare")
def compare_ceos(request: CompareRequest):
    """
    Compare a list of CEO IDs and return similarity scores and deltas.
    """
    if len(request.ids) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 IDs to compare")
    
    # Get embedding engine
    emb_engine = get_embedding_engine()
    
    # Fetch vectors
    vectors = []
    for ceo_id in request.ids:
        vec = emb_engine.get_vector_for_ceo(ceo_id)
        if vec is None:
            # Try to fetch CEO data and compute vector
            if DB_AVAILABLE:
                try:
                    # Get CEO name
                    ceo_rows = fetch_rows("SELECT name FROM ceos WHERE id = ?", (ceo_id,))
                    if not ceo_rows:
                        raise HTTPException(status_code=404, detail=f"CEO with ID {ceo_id} not found")
                    
                    ceo_name = ceo_rows[0]["name"]
                    
                    # Get profile facts
                    facts = fetch_rows("""
                        SELECT pf.pillar, pf.field, pf.value 
                        FROM profile_facts pf
                        JOIN ceo_profile_versions cpv ON pf.profile_version_id = cpv.id
                        WHERE cpv.ceo_id = ?
                    """, (ceo_id,))
                    
                    # Combine facts into a profile text
                    profile_text = f"CEO: {ceo_name}\n"
                    for fact in facts:
                        profile_text += f"{fact['pillar']}.{fact['field']}: {fact['value']}\n"
                    
                    # Compute and store vector
                    vec = emb_engine.compute_and_store_vector_for_profile_version(profile_text, ceo_id)
                    
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Error computing vector: {str(e)}")
            
            if vec is None:
                raise HTTPException(status_code=404, detail=f"Vector not found for CEO {ceo_id}")
        
        vectors.append((ceo_id, vec))
    
    # Compute pairwise similarities
    similarities = emb_engine.pairwise_similarity(vectors)
    
    # Get deltas (placeholder - would need to fetch actual profile facts to compute real deltas)
    deltas = {}
    for i in range(len(request.ids)):
        for j in range(i+1, len(request.ids)):
            ceo_a = request.ids[i]
            ceo_b = request.ids[j]
            pair_key = f"{ceo_a}|{ceo_b}"
            
            # Find similarity score for this pair
            sim_score = 0.5  # Default
            for sim in similarities:
                if sim["pair"] == pair_key:
                    sim_score = sim["similarity"]
                    break
            
            deltas[pair_key] = {
                "strategic_philosophy": {"similarity": sim_score * 0.9},  # Slightly different per pillar
                "leadership_style": {"similarity": sim_score * 1.1},
                "operational_cadence": {"similarity": sim_score * 0.8},
                "personal_ethos": {"similarity": sim_score * 1.2}
            }
    
    return {"similarities": similarities, "deltas": deltas}

@app.post("/api/query")
def query_api(request: QueryRequest):
    """
    Process a natural language query and return relevant CEOs and confidence scores.
    """
    # Get embedding engine
    emb_engine = get_embedding_engine()
    
    # Embed the query
    query_vec = emb_engine.embed_text(request.query)
    
    # Find nearest CEOs
    results = emb_engine.get_nearest(query_vec, k=request.top_k)
    
    # Enhance results with CEO names if database is available
    if DB_AVAILABLE:
        for result in results:
            ceo_id = result["ceo_id"]
            try:
                ceo_rows = fetch_rows("SELECT name FROM ceos WHERE id = ?", (ceo_id,))
                if ceo_rows:
                    result["name"] = ceo_rows[0]["name"]
            except Exception:
                pass
    
    return {
        "query": request.query,
        "results": results,
        "intent": "ceo_similarity",  # Placeholder for more sophisticated intent detection
        "filters": {}  # Placeholder for extracted filters
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)