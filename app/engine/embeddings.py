# app/engine/embeddings.py
from sentence_transformers import SentenceTransformer, util
import numpy as np
from typing import List, Tuple, Any, Dict, Optional
import json
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to import database connection
try:
    from app.db.connection import get_db_conn
    DB_AVAILABLE = True
except ImportError:
    logger.warning("Database connection not available")
    DB_AVAILABLE = False

class EmbeddingEngine:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Try to load the model
        try:
            self.model = SentenceTransformer(model_name)
            logger.info(f"Loaded sentence transformer model: {model_name}")
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {e}")
            self.model = None
            
        # Cache for vectors
        self._cache = {}
        
        # Load vectors from DB if available
        if DB_AVAILABLE:
            self._load_vectors_from_db()

    def _load_vectors_from_db(self):
        """Load vectors from database into memory cache"""
        try:
            conn = get_db_conn()
            cur = conn.cursor()
            cur.execute("SELECT ceo_id, vector_json FROM ceo_vectors")
            rows = cur.fetchall()
            for row in rows:
                ceo_id, vjson = row
                try:
                    vec = np.array(json.loads(vjson), dtype=float)
                    self._cache[int(ceo_id)] = vec
                except Exception as e:
                    logger.error(f"Error loading vector for CEO {ceo_id}: {e}")
            logger.info(f"Loaded {len(self._cache)} vectors from database")
        except Exception as e:
            logger.error(f"Error loading vectors from database: {e}")

    def embed_text(self, text: str) -> Optional[np.ndarray]:
        """Embed text using the sentence transformer model"""
        if not text or self.model is None:
            return np.zeros(384)  # Default dimension for all-MiniLM-L6-v2
        
        try:
            v = self.model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
            return v
        except Exception as e:
            logger.error(f"Error embedding text: {e}")
            return np.zeros(384)

    def add_vector_for_ceo(self, ceo_id: int, vector: np.ndarray) -> bool:
        """Store a vector for a CEO in the database and cache"""
        if not DB_AVAILABLE:
            logger.warning("Database not available, vector not stored")
            self._cache[ceo_id] = vector
            return False
            
        try:
            conn = get_db_conn()
            cur = conn.cursor()
            vjson = json.dumps(vector.tolist())
            cur.execute("INSERT OR REPLACE INTO ceo_vectors (ceo_id, vector_json) VALUES (?, ?)", 
                       (ceo_id, vjson))
            conn.commit()
            self._cache[ceo_id] = vector
            return True
        except Exception as e:
            logger.error(f"Error storing vector for CEO {ceo_id}: {e}")
            return False

    def get_vector_for_ceo(self, ceo_id: int) -> Optional[np.ndarray]:
        """Get the vector for a CEO from cache or database"""
        # Check cache first
        if ceo_id in self._cache:
            return self._cache[ceo_id]
            
        # Try to load from database
        if DB_AVAILABLE:
            try:
                conn = get_db_conn()
                cur = conn.cursor()
                cur.execute("SELECT vector_json FROM ceo_vectors WHERE ceo_id = ?", (ceo_id,))
                row = cur.fetchone()
                if row:
                    vjson = row[0]
                    vec = np.array(json.loads(vjson), dtype=float)
                    self._cache[ceo_id] = vec
                    return vec
            except Exception as e:
                logger.error(f"Error loading vector for CEO {ceo_id}: {e}")
                
        return None

    def get_nearest(self, qvec: np.ndarray, k: int = 10) -> List[Dict[str, Any]]:
        """Find the nearest CEO vectors to a query vector"""
        items = []
        for cid, vec in self._cache.items():
            sim = float(np.dot(qvec, vec) / (np.linalg.norm(qvec) * np.linalg.norm(vec) + 1e-10))
            items.append((cid, sim))
        items.sort(key=lambda x: x[1], reverse=True)
        return [{"ceo_id": cid, "score": score} for cid, score in items[:k]]

    def pairwise_similarity(self, id_vector_pairs: List[Tuple[int, np.ndarray]]) -> List[Dict[str, Any]]:
        """Compute pairwise similarities between CEO vectors"""
        pairs = []
        for i in range(len(id_vector_pairs)):
            for j in range(i + 1, len(id_vector_pairs)):
                a_id, a_vec = id_vector_pairs[i]
                b_id, b_vec = id_vector_pairs[j]
                sim = float(np.dot(a_vec, b_vec) / (np.linalg.norm(a_vec) * np.linalg.norm(b_vec) + 1e-10))
                pairs.append({"pair": f"{a_id}|{b_id}", "similarity": sim})
        return pairs

    def compute_and_store_vector_for_profile_version(self, profile_text: str, ceo_id: int) -> Optional[np.ndarray]:
        """Compute and store a vector for a CEO profile text"""
        vec = self.embed_text(profile_text)
        success = self.add_vector_for_ceo(ceo_id, vec)
        if success:
            logger.info(f"Stored vector for CEO {ceo_id}")
        return vec


# Singleton instance
_embedding_engine = None

def get_embedding_engine() -> EmbeddingEngine:
    """Get or create the singleton embedding engine instance"""
    global _embedding_engine
    if _embedding_engine is None:
        _embedding_engine = EmbeddingEngine()
    return _embedding_engine