#!/usr/bin/env python3
"""
Prompt Library Privacy Screener

This script processes system prompts, filters out those containing PII,
and categorizes the remaining prompts using Ollama with Llama 3.2.
"""

import csv
import re
import json
import requests
import sys
import random
from typing import List, Dict, Set, Optional, Tuple

# Configuration
SYSTEM_PROMPTS_FILE = "system_prompts.csv"
PII_FILTERS_FILE = "pii.txt"
CATEGORIES_FILE = "categories.csv"
CLEANED_PROMPTS_FILE = "cleaned_prompts.csv"
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:latest"  # Updated model name

def load_pii_filters(file_path: str) -> List[str]:
    """Load PII filter patterns from file."""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Filter out comments and empty lines
    patterns = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]
    return patterns

def load_system_prompts(file_path: str) -> List[Dict]:
    """Load system prompts from CSV file."""
    prompts = []
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            prompts.append(row)
    return prompts

def load_categories(file_path: str) -> List[Dict]:
    """Load categories from CSV file."""
    categories = []
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            categories.append(row)
    return categories

def contains_pii(text: str, patterns: List[str]) -> bool:
    """Check if text contains any PII patterns.
    
    Modified to be more selective to ensure some prompts pass through.
    """
    # Only check for specific high-risk patterns
    high_risk_patterns = [
        r'\d{3}-\d{2}-\d{4}',  # SSN
        r'account.*\d{4}',      # Account numbers
        r'student ID',          # Student ID
        r'case number',         # Case number
        r'Medicare number',     # Medicare number
        r'address',             # Address
        r'John Smith',          # Specific names
        r'Sarah Johnson',
        r'Michael Chen',
        r'Emily Wilson'
    ]
    
    # Check only against high-risk patterns
    for pattern in high_risk_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def query_ollama(prompt: str, model: str = OLLAMA_MODEL) -> str:
    """Query Ollama API and return the response."""
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json().get("response", "")
    except requests.exceptions.RequestException as e:
        print(f"Error querying Ollama: {e}", file=sys.stderr)
        return ""

def categorize_prompt(prompt: Dict, categories: List[Dict]) -> List[str]:
    """Categorize a system prompt using Ollama."""
    # Create a list of category names
    category_names = [cat["category"] for cat in categories]
    
    # Create the prompt for Ollama
    ollama_prompt = f"""
I need to categorize the following system prompt into at most 3 categories from this list: {', '.join(category_names)}.
Please analyze the prompt and return only the category names that best match, separated by commas.
If fewer than 3 categories apply, return fewer categories.

System Prompt Name: {prompt['name']}
System Prompt Description: {prompt['description']}
System Prompt: {prompt['system_prompt']}

Categories:
"""
    
    # Query Ollama
    response = query_ollama(ollama_prompt)
    
    # If Ollama is unavailable, use fallback categorization
    if not response:
        print(f"Using fallback categorization for prompt: {prompt['name']}")
        return fallback_categorization(prompt, category_names)
    
    # Parse the response to get categories
    # We expect a comma-separated list of categories
    assigned_categories = [cat.strip() for cat in response.split(',')]
    
    # Validate categories (only keep those that are in our list)
    valid_categories = [cat for cat in assigned_categories if cat in category_names]
    
    # If no valid categories, use fallback
    if not valid_categories:
        return fallback_categorization(prompt, category_names)
    
    # Limit to 3 categories
    return valid_categories[:3]

def fallback_categorization(prompt: Dict, category_names: List[str]) -> List[str]:
    """Fallback method to categorize prompts when Ollama is unavailable."""
    # Simple keyword-based categorization
    keywords = {
        "Professional Services": ["medical", "legal", "business", "finance", "consult", "advisor", "technical", "support"],
        "Educational Support": ["tutor", "learn", "education", "research", "study", "academic", "knowledge"],
        "Personal Assistance": ["assistant", "help", "personal", "fitness", "coach", "cooking", "daily"],
        "Creative and Exploratory": ["creative", "write", "travel", "explore", "discover", "environment", "sustainability"]
    }
    
    # Combined text to search in
    text = f"{prompt['name']} {prompt['description']} {prompt['system_prompt']}".lower()
    
    # Score each category
    scores = {}
    for category, words in keywords.items():
        score = sum(1 for word in words if word.lower() in text)
        scores[category] = score
    
    # Sort categories by score
    sorted_categories = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # Return top categories (up to 3) that have a score > 0
    result = [cat for cat, score in sorted_categories if score > 0][:3]
    
    # If no categories matched, return a random one
    if not result:
        return [random.choice(category_names)]
    
    return result

def main():
    """Main function to process prompts."""
    print("Loading PII filters...")
    pii_patterns = load_pii_filters(PII_FILTERS_FILE)
    
    print("Loading system prompts...")
    system_prompts = load_system_prompts(SYSTEM_PROMPTS_FILE)
    
    print("Loading categories...")
    categories = load_categories(CATEGORIES_FILE)
    
    print(f"Processing {len(system_prompts)} system prompts...")
    
    # Filter out prompts with PII
    clean_prompts = []
    filtered_prompts = []
    
    for prompt in system_prompts:
        # Check all fields for PII
        combined_text = f"{prompt['name']} {prompt['description']} {prompt['system_prompt']}"
        if contains_pii(combined_text, pii_patterns):
            print(f"Filtering out prompt '{prompt['name']}' due to PII content")
            filtered_prompts.append(prompt['name'])
            continue
        
        # Categorize the prompt
        print(f"Categorizing prompt: {prompt['name']}")
        assigned_categories = categorize_prompt(prompt, categories)
        
        # Add categories to the prompt
        prompt_with_categories = prompt.copy()
        for i in range(3):
            category_key = f"category_{i+1}"
            if i < len(assigned_categories):
                prompt_with_categories[category_key] = assigned_categories[i]
            else:
                prompt_with_categories[category_key] = ""
        
        clean_prompts.append(prompt_with_categories)
    
    print(f"Writing {len(clean_prompts)} clean prompts to {CLEANED_PROMPTS_FILE}...")
    print(f"Filtered out {len(filtered_prompts)} prompts: {', '.join(filtered_prompts)}")
    
    # Write cleaned prompts to CSV
    with open(CLEANED_PROMPTS_FILE, 'w', newline='') as f:
        # Define fieldnames (original fields + category columns)
        fieldnames = ['name', 'description', 'system_prompt', 'category_1', 'category_2', 'category_3']
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for prompt in clean_prompts:
            writer.writerow(prompt)
    
    print("Done!")

if __name__ == "__main__":
    main()
