"""
Script to analyze Fortune 500 CEO list and add missing CEOs to our knowledgebase.
"""

import csv
import os
import sys
from pathlib import Path

# Add parent directory to path to import repository module
sys.path.append(str(Path(__file__).parent.parent.parent))
from app.repository.store import load_repository


def load_fortune500_ceos(csv_path):
    """Load Fortune 500 CEOs from CSV file."""
    ceos = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ceos.append(row)
    return ceos


def load_existing_ceos():
    """Load existing CEOs from the repository."""
    repo = load_repository()
    return repo.list_ceo_names()


def find_missing_ceos(fortune500_ceos, existing_ceos):
    """Find CEOs that are in Fortune 500 list but not in our knowledgebase."""
    fortune500_names = [ceo['name'] for ceo in fortune500_ceos]
    missing_ceos = []
    
    for ceo in fortune500_ceos:
        name = ceo['name']
        if name not in existing_ceos:
            missing_ceos.append(ceo)
    
    return missing_ceos


def create_ceo_entry(ceo):
    """Create a CSV entry for a new CEO."""
    return f'"{ceo["name"]}","TBD - {ceo["name"]} core ideology","TBD - market positioning","TBD - innovation engine","TBD - competitive stance","TBD - risk profile","TBD - hiring philosophy","TBD - culture","TBD - motivation","TBD - communication","TBD - talent","TBD - meetings","TBD - decisions","TBD - metrics","TBD - focus","TBD - accountability","TBD - principles","TBD - work ethic","TBD - learning","TBD - resilience"'


def append_missing_ceos(missing_ceos, ceos_csv_path):
    """Append missing CEOs to the ceos.csv file."""
    with open(ceos_csv_path, 'a', encoding='utf-8') as f:
        for ceo in missing_ceos:
            f.write('\n' + create_ceo_entry(ceo))
    
    return len(missing_ceos)


def main():
    # Define file paths
    base_dir = Path(__file__).parent.parent.parent
    fortune500_csv_path = base_dir / 'data' / 'fortune500_ceos.csv'
    ceos_csv_path = base_dir / 'data' / 'ceos.csv'
    
    # Load data
    fortune500_ceos = load_fortune500_ceos(fortune500_csv_path)
    existing_ceos = load_existing_ceos()
    
    # Find missing CEOs
    missing_ceos = find_missing_ceos(fortune500_ceos, existing_ceos)
    
    # Print summary
    print(f"Total Fortune 500 CEOs: {len(fortune500_ceos)}")
    print(f"Existing CEOs in knowledgebase: {len(existing_ceos)}")
    print(f"Missing CEOs: {len(missing_ceos)}")
    
    # Append missing CEOs if any
    if missing_ceos:
        count = append_missing_ceos(missing_ceos, ceos_csv_path)
        print(f"Added {count} new CEOs to the knowledgebase.")
        print("New CEOs added:")
        for ceo in missing_ceos:
            print(f"- {ceo['name']} ({ceo['company']}, {ceo['industry']})")
    else:
        print("No missing CEOs found.")


if __name__ == "__main__":
    main()
