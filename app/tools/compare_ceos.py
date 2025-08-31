"""
CEO Comparison Tool - Analyze similarities between CEOs based on their profiles and situations.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import argparse
from collections import Counter
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Add parent directory to path to import repository module
sys.path.append(str(Path(__file__).parent.parent.parent))
from app.repository.store import Repository


def load_repository() -> Repository:
    """Load the CEO repository."""
    from app.repository.store import load_repository
    return load_repository()


def get_ceo_text_profile(repo: Repository, ceo_name: str) -> str:
    """Get a text representation of a CEO's profile for comparison."""
    ceo = repo.get_ceo(ceo_name)
    if not ceo:
        return ""
    
    texts = []
    
    # Extract all text fields from the CEO profile
    for pillar in ["strategic_philosophy", "leadership", "operational_cadence", "personal_ethos"]:
        if pillar in ceo:
            for field, value in ceo[pillar].items():
                if value and isinstance(value, str) and "TBD" not in value:
                    texts.append(value)
    
    return " ".join(texts)


def get_ceo_situations(repo: Repository, ceo_name: str) -> List[Dict[str, Any]]:
    """Get all situations for a CEO."""
    all_situations = repo._situations
    return [s for s in all_situations if s.get("ceo") == ceo_name]


def get_situation_tags(situations: List[Dict[str, Any]]) -> Counter:
    """Extract and count situation tags."""
    tags = []
    for situation in situations:
        if "tags" in situation:
            tags.extend([tag.split(":", 1)[1] if ":" in tag else tag 
                         for tag in situation.get("tags", [])])
    return Counter(tags)


def calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate cosine similarity between two text strings."""
    if not text1 or not text2:
        return 0.0
    
    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    except:
        return 0.0


def calculate_tag_similarity(tags1: Counter, tags2: Counter) -> float:
    """Calculate Jaccard similarity between two sets of tags."""
    if not tags1 or not tags2:
        return 0.0
    
    set1 = set(tags1.keys())
    set2 = set(tags2.keys())
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    if union == 0:
        return 0.0
    
    return intersection / union


def find_similar_ceos(repo: Repository, ceo_name: str, top_k: int = 5) -> List[Tuple[str, float, Dict[str, float]]]:
    """Find CEOs similar to the specified CEO."""
    target_ceo_text = get_ceo_text_profile(repo, ceo_name)
    target_situations = get_ceo_situations(repo, ceo_name)
    target_tags = get_situation_tags(target_situations)
    
    if not target_ceo_text:
        print(f"Error: CEO '{ceo_name}' not found or has no profile data.")
        return []
    
    similarities = []
    all_ceos = repo.list_ceo_names()
    
    for other_ceo in all_ceos:
        if other_ceo == ceo_name:
            continue
        
        other_ceo_text = get_ceo_text_profile(repo, other_ceo)
        if not other_ceo_text or "TBD" in other_ceo_text:
            continue  # Skip CEOs with placeholder data
            
        other_situations = get_ceo_situations(repo, other_ceo)
        other_tags = get_situation_tags(other_situations)
        
        # Calculate similarities
        text_sim = calculate_text_similarity(target_ceo_text, other_ceo_text)
        tag_sim = calculate_tag_similarity(target_tags, other_tags)
        
        # Calculate overall similarity (weighted average)
        overall_sim = 0.7 * text_sim + 0.3 * tag_sim
        
        similarities.append((other_ceo, overall_sim, {
            "profile_similarity": text_sim,
            "situation_similarity": tag_sim
        }))
    
    # Sort by overall similarity
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_k]


def find_common_principles(repo: Repository, ceo1: str, ceo2: str) -> Dict[str, List[Tuple[str, str]]]:
    """Find common principles between two CEOs."""
    profile1 = repo.get_ceo(ceo1)
    profile2 = repo.get_ceo(ceo2)
    
    if not profile1 or not profile2:
        return {}
    
    common_principles = {}
    
    # Compare each pillar and field
    for pillar in ["strategic_philosophy", "leadership", "operational_cadence", "personal_ethos"]:
        if pillar not in profile1 or pillar not in profile2:
            continue
            
        for field in profile1[pillar]:
            if field not in profile2[pillar]:
                continue
                
            value1 = profile1[pillar][field]
            value2 = profile2[pillar][field]
            
            if not value1 or not value2 or "TBD" in value1 or "TBD" in value2:
                continue
                
            # Find common keywords or phrases
            keywords1 = set(re.findall(r'\b\w+\b', value1.lower()))
            keywords2 = set(re.findall(r'\b\w+\b', value2.lower()))
            
            common_words = keywords1.intersection(keywords2)
            common_words = {w for w in common_words if len(w) > 3 and w not in 
                           {'with', 'that', 'this', 'from', 'have', 'what', 'when', 'where', 'which', 'their', 'there'}}
            
            if common_words:
                key = f"{pillar}.{field}"
                common_principles[key] = [(value1, value2)]
    
    return common_principles


def print_ceo_comparison(repo: Repository, ceo_name: str, similar_ceos: List[Tuple[str, float, Dict[str, float]]]) -> None:
    """Print comparison results between a CEO and similar CEOs."""
    print(f"\n=== CEOs Similar to {ceo_name} ===\n")
    
    for i, (similar_ceo, overall_sim, sim_details) in enumerate(similar_ceos, 1):
        print(f"{i}. {similar_ceo} (Similarity: {overall_sim:.2f})")
        print(f"   - Profile Similarity: {sim_details['profile_similarity']:.2f}")
        print(f"   - Situation Similarity: {sim_details['situation_similarity']:.2f}")
        
        # Find common principles
        common = find_common_principles(repo, ceo_name, similar_ceo)
        if common:
            print(f"   - Common Principles:")
            for key, values in common.items():
                print(f"     * {key}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Compare CEOs based on their profiles and situations")
    parser.add_argument("ceo", help="Name of the CEO to compare")
    parser.add_argument("--top-k", type=int, default=5, help="Number of similar CEOs to show")
    args = parser.parse_args()
    
    repo = load_repository()
    similar_ceos = find_similar_ceos(repo, args.ceo, args.top_k)
    print_ceo_comparison(repo, args.ceo, similar_ceos)


if __name__ == "__main__":
    main()
