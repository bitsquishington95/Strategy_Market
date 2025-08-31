"""
CEO Visualization Tool - Create visual representations of CEO similarities and clusters.
"""

import sys
import os
from pathlib import Path
import argparse
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
import matplotlib.colors as mcolors
import matplotlib.cm as cm

# Add parent directory to path to import repository module
sys.path.append(str(Path(__file__).parent.parent.parent))
from app.repository.store import load_repository
from app.tools.compare_ceos import get_ceo_text_profile


def create_ceo_vectors(min_enriched_ceos=10):
    """Create vector representations of CEO profiles."""
    repo = load_repository()
    ceo_names = repo.list_ceo_names()
    
    # Get text profiles for each CEO
    ceo_texts = {}
    for name in ceo_names:
        text = get_ceo_text_profile(repo, name)
        if text and "TBD" not in text:  # Only include enriched CEOs
            ceo_texts[name] = text
    
    if len(ceo_texts) < min_enriched_ceos:
        print(f"Warning: Only {len(ceo_texts)} enriched CEO profiles found. Need at least {min_enriched_ceos}.")
        return None, None
    
    # Convert to list for vectorization
    names = list(ceo_texts.keys())
    texts = [ceo_texts[name] for name in names]
    
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(max_features=100)
    vectors = vectorizer.fit_transform(texts)
    
    return names, vectors


def visualize_ceo_clusters(output_file=None, min_ceos=10):
    """Create a 2D visualization of CEO clusters."""
    names, vectors = create_ceo_vectors(min_enriched_ceos=min_ceos)
    if names is None or vectors is None:
        return False
    
    # Use t-SNE to reduce dimensions to 2D
    tsne = TSNE(n_components=2, random_state=42, perplexity=min(5, len(names)-1))
    vectors_2d = tsne.fit_transform(vectors.toarray())
    
    # Create industry categories based on keywords in profiles
    industries = []
    repo = load_repository()
    for name in names:
        ceo = repo.get_ceo(name)
        if not ceo or "strategic_philosophy" not in ceo:
            industries.append("Unknown")
            continue
            
        mp = ceo["strategic_philosophy"].get("market_positioning", "")
        if not mp or "TBD" in mp:
            industries.append("Unknown")
            continue
            
        # Extract industry keywords
        mp_lower = mp.lower()
        if any(kw in mp_lower for kw in ["tech", "software", "platform", "computing"]):
            industries.append("Technology")
        elif any(kw in mp_lower for kw in ["retail", "consumer"]):
            industries.append("Retail")
        elif any(kw in mp_lower for kw in ["financial", "bank"]):
            industries.append("Finance")
        elif any(kw in mp_lower for kw in ["auto", "car"]):
            industries.append("Automotive")
        elif any(kw in mp_lower for kw in ["media", "entertainment"]):
            industries.append("Media")
        elif any(kw in mp_lower for kw in ["food", "coffee", "restaurant"]):
            industries.append("Food Service")
        elif any(kw in mp_lower for kw in ["oil", "steel", "manufacturing"]):
            industries.append("Manufacturing")
        else:
            industries.append("Other")
    
    # Plot the results
    plt.figure(figsize=(12, 8))
    
    # Create a colormap for industries
    unique_industries = list(set(industries))
    colors = plt.cm.tab10(np.linspace(0, 1, len(unique_industries)))
    industry_colors = {ind: colors[i] for i, ind in enumerate(unique_industries)}
    
    # Plot each CEO as a point
    for i, (name, industry) in enumerate(zip(names, industries)):
        x, y = vectors_2d[i]
        plt.scatter(x, y, color=industry_colors[industry], s=100, alpha=0.7)
        plt.annotate(name, (x, y), fontsize=9, 
                    xytext=(5, 5), textcoords='offset points')
    
    # Add a legend for industries
    for industry, color in industry_colors.items():
        plt.scatter([], [], color=color, label=industry)
    plt.legend(title="Industry", loc="best")
    
    plt.title("CEO Similarity Map")
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Visualization saved to {output_file}")
    else:
        plt.show()
    
    return True


def create_similarity_heatmap(ceo_names=None, output_file=None):
    """Create a heatmap of CEO similarities."""
    repo = load_repository()
    
    if ceo_names is None:
        # Get all enriched CEOs
        all_ceos = repo.list_ceo_names()
        ceo_names = []
        for name in all_ceos:
            text = get_ceo_text_profile(repo, name)
            if text and "TBD" not in text:
                ceo_names.append(name)
    
    if len(ceo_names) < 2:
        print("Need at least 2 CEOs for comparison.")
        return False
    
    # Get text profiles
    texts = []
    for name in ceo_names:
        text = get_ceo_text_profile(repo, name)
        texts.append(text if text else "")
    
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(texts)
    
    # Calculate cosine similarities
    similarity_matrix = (vectors @ vectors.T).toarray()
    
    # Plot heatmap
    plt.figure(figsize=(10, 8))
    plt.imshow(similarity_matrix, cmap='viridis')
    
    # Add labels
    plt.xticks(range(len(ceo_names)), ceo_names, rotation=90)
    plt.yticks(range(len(ceo_names)), ceo_names)
    
    # Add colorbar and title
    plt.colorbar(label='Similarity')
    plt.title('CEO Profile Similarity Heatmap')
    
    # Add values in cells
    for i in range(len(ceo_names)):
        for j in range(len(ceo_names)):
            plt.text(j, i, f"{similarity_matrix[i, j]:.2f}", 
                    ha="center", va="center", 
                    color="white" if similarity_matrix[i, j] > 0.5 else "black")
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Heatmap saved to {output_file}")
    else:
        plt.show()
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Visualize CEO similarities and clusters")
    parser.add_argument("--output", help="Output file path for visualization (PNG format)")
    parser.add_argument("--type", choices=["cluster", "heatmap"], default="cluster",
                       help="Type of visualization to create")
    parser.add_argument("--ceos", nargs="+", help="Specific CEOs to include in heatmap")
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    
    if args.type == "cluster":
        visualize_ceo_clusters(args.output)
    else:  # heatmap
        create_similarity_heatmap(args.ceos, args.output)


if __name__ == "__main__":
    main()
