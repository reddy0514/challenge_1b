import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import fitz 
DEFAULT_COLLECTIONS_DIR = "."
MAX_OUTPUT_ITEMS = 5

def extract_keywords(text: str) -> List[str]:

    text = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())
    return [word for word in text.split() if len(word) > 3]

def refine_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text.strip())
    return text[:500] + ("..." if len(text) > 500 else "")

def read_pdf_by_page(pdf_path: str) -> Dict[int, str]:
    text_by_page = {}
    doc = fitz.open(pdf_path)
    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        text = page.get_text().strip()
        if text:
            text_by_page[page_number + 1] = text
    return text_by_page

def score_text(text: str, keywords: List[str]) -> int:
    text = text.lower()
    return sum(text.count(k) for k in keywords)

def identify_dietary_needs(text: str) -> List[str]:
    dietary_needs = []
    common_restrictions = [
        'vegetarian', 'vegan', 'gluten-free', 'dairy-free', 
        'nut-free', 'kosher', 'halal', 'low-carb', 'keto'
    ]
    for restriction in common_restrictions:
        if restriction in text.lower():
            dietary_needs.append(restriction)
    return dietary_needs

def extract_recipes_from_text(text: str) -> List[Dict[str, str]]:
    """Extract recipes from text content."""
    recipes = []
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    i = 0
    while i < len(lines):
        if "recipe" in lines[i].lower() or "ingredients" in lines[i].lower():
            recipe = {
                "title": lines[i],
                "ingredients": [],
                "instructions": []
            }
            i += 1
        
            while i < len(lines) and ("instruction" not in lines[i].lower() and "method" not in lines[i].lower()):
                if lines[i]:
                    recipe["ingredients"].append(lines[i])
                i += 1
        
            while i < len(lines) and not ("recipe" in lines[i].lower() or "ingredients" in lines[i].lower()):
                if lines[i]:
                    recipe["instructions"].append(lines[i])
                i += 1
            
            recipes.append(recipe)
        else:
            i += 1
    
    return recipes

def meets_dietary_requirements(recipe: Dict[str, List[str]], dietary_needs: List[str]) -> bool:
    if not dietary_needs:
        return True
    
    recipe_text = " ".join([recipe["title"]] + recipe["ingredients"]).lower()
    
    for need in dietary_needs:
        if need=="vegetarian":
            non_veg = ["meat", "beef", "pork", "chicken", "fish", "lamb"]
            if any(item in recipe_text for item in non_veg):
                return False
        elif need =="vegan":
            non_vegan = ["meat", "dairy", "cheese", "milk", "egg", "honey"]
            if any(item in recipe_text for item in non_vegan):
                return False
        elif need not in recipe_text:
            return False
    
    return True

def extract_section_title(lines: List[str]) -> str:
    for line in lines:
        if line.isupper() and len(line.split()) <= 10:
            return line
    return lines[0] if lines else "Untitled Section"
def process_collection(collection_path: Path):
    print(f"\nProcessing {collection_path.name}...")

    try:
        input_file=collection_path/"challenge1b_input.json"
        with open(input_file, "r", encoding="utf-8") as f:
            config=json.load(f)

        persona=config["persona"]["role"]
        task=config["job_to_be_done"]["task"]
        documents=config["documents"]

        keywords=extract_keywords(task)
        extracted_sections=[]
        subsection_analysis=[]

        pdf_dir=collection_path / "PDFs"
        for doc in documents:
            filename=doc["filename"]
            pdf_path=pdf_dir / filename
            if not pdf_path.exists():
                print(f"  Warning: File not found - {filename}")
                continue

            pages=read_pdf_by_page(str(pdf_path))
            for page_num, text in pages.items():
                lines=[line.strip() for line in text.split('\n') if line.strip()]
                title=extract_section_title(lines)
                score=score_text(text, keywords)

                extracted_sections.append({
                    "document": filename,
                    "section_title": title,
                    "importance_rank": score,
                    "page_number": page_num
                })

                subsection_analysis.append({
                    "document": filename,
                    "refined_text": refine_text(text),
                    "page_number": page_num
                })

        extracted_sections.sort(key=lambda x:x["importance_rank"], reverse=True)
        subsection_analysis.sort(key=lambda x:x["page_number"])

        output_data={
            "metadata": {
                "input_documents": [doc["filename"] for doc in documents],
                "persona": persona,
                "job_to_be_done": task,
                "processing_timestamp": datetime.now().isoformat()
            },
            "extracted_sections": extracted_sections[:MAX_OUTPUT_ITEMS],
            "subsection_analysis": subsection_analysis[:MAX_OUTPUT_ITEMS]
        }

        output_file=collection_path/"challenge1b_output.json"
        with open(output_file,"w",encoding="utf-8") as f:
            json.dump(output_data,f,indent=2,ensure_ascii=False)

        print(f"  Successfully processed {len(documents)} documents")

    except Exception as e:
        print(f"  Error processing collection: {str(e)}")
def main():
    collections_dir = os.getenv("COLLECTIONS_DIR", DEFAULT_COLLECTIONS_DIR)
    collection_paths = [p for p in Path(collections_dir).iterdir()
                        if p.is_dir() and p.name.startswith("Collection")]
    if not collection_paths:
        print(f"No collections found in {collections_dir}")
        return
    print(f"\nFound {len(collection_paths)} collections to process:")
    for path in collection_paths:
        print(f"  - {path.name}")
    for collection_path in collection_paths:
        process_collection(collection_path)
if __name__=="__main__":
    main()
