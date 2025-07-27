Adobe Hackathon - Multi-Collection PDF Analyzer

Purpose
-------
This script analyzes multiple PDF collections based on a given persona and task (like finding dietary-specific recipes or extracting key content). It processes each PDF, scores its relevance using extracted keywords, summarizes content, and outputs the results in structured JSON files.

Libraries Used
--------------
- os        : Access environment variables, handle file paths
- re        : Regular expressions for cleaning and searching text
- json      : Reading/writing JSON files
- datetime  : Timestamps
- pathlib   : File and folder path handling
- typing    : Type hinting (List, Dict, etc.)
- fitz (PyMuPDF): PDF text extraction

To install PyMuPDF:
    pip install pymupdf

Folder Structure
----------------
Your directory should be structured like this:

.
├── Collection1/
│   ├── challenge1b_input.json
│   └── PDFs/
│       ├── file01.pdf
│       └── file02.pdf
├── Collection2/
│   ├── challenge1b_input.json
│   └── PDFs/
│       └── ...
└── analyzer.py

Each Collection folder contains:
- challenge1b_input.json : Includes persona, task, and documents
- PDFs/ : Folder containing the actual PDF files

How It Works
------------
1. main()
   - Entry point
   - Finds all Collection folders
   - Calls process_collection() on each one

2. Reads challenge1b_input.json:
   - persona: e.g., "Nutritionist"
   - job_to_be_done: e.g., "Find vegan high-protein recipes"
   - documents: list of filenames

3. extract_keywords(task)
   - Cleans text
   - Extracts keywords longer than 3 characters

4. read_pdf_by_page(pdf_path)
   - Uses PyMuPDF
   - Extracts text from each page
   - Returns a dictionary of {page_number: page_text}

5. score_text(text, keywords)
   - Scores text based on keyword frequency

6. extract_section_title(lines)
   - Looks for uppercase lines as titles
   - Defaults to the first line if no suitable title found

7. extract_recipes_from_text(text)
   - Looks for lines containing "recipe", "ingredients", or "instructions"
   - Builds dictionary of ingredients and steps

8. identify_dietary_needs(text) and meets_dietary_requirements(recipe, needs)
   - Identifies dietary needs like "vegan", "gluten-free", etc.
   - Filters recipes that violate those needs

9. Output
   - Writes challenge1b_output.json in each collection folder
   - Includes:
       - metadata
       - extracted_sections (top ranked)
       - subsection_analysis (trimmed summaries)

Example Output
--------------
{
  "metadata": {
    "persona": "Nutritionist",
    "job_to_be_done": "Find vegan high-protein recipes",
    "processing_timestamp": "2025-07-27T12:45:00"
  },
  "extracted_sections": [
    {
      "document": "file01.pdf",
      "section_title": "VEGAN PROTEIN RECIPES",
      "importance_rank": 8,
      "page_number": 3
    }
  ],
  "subsection_analysis": [
    {
      "document": "file01.pdf",
      "refined_text": "These recipes focus on beans, tofu, and lentils as primary protein sources...",
      "page_number": 3
    }
  ]
}

How to Run
----------
1. Install dependencies:
    pip install pymupdf

2. Place PDFs and challenge1b_input.json inside Collection folders

3. Run the script:
    python analyzer.py

Summary
-------
- Works on multiple collections
- Extracts and ranks relevant PDF content
- Filters based on persona needs and task
- Outputs JSON with metadata, ranked sections, and summaries

Optional Enhancements
---------------------
- Export as PDF
- Highlight keywords in text
- Add visual summaries
