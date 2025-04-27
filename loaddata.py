import fitz  # PyMuPDF
import csv
import os
import re

# --- Settings ---
pdf_folder = "/Users/annemoll/Desktop/jobs/pdffiles"  # <-- set this to your folder containing PDFs
csv_path = "job_descriptions.csv"

# Noise we want to remove
noise_phrases = [
    "Startside", "Log på", "Gennemse jobs", "Om Indeed", "Impressum", "Cookies",
    "Vilkår", "Privatlivscenter", "Rapportér job", "Tilgængelighed", "Side om onlinesikkerhed",
    "Ansøg nu", "Ansøg her", "Ansøgning", "Jobtype", "Arbejdssted", "Arbejdstid", "Jobområde", "Lokation",
]

# Phrases we don't want treated as titles
bad_titles = {
    "Jobdetaljer", "Komplet jobbeskrivelse", "Fakta", "Spørgsmål og ansøgning",
}

# Function to fix bad encoding
def fix_encoding(text):
    replacements = {
        "√∏": "ø", "√•": "å", "√¶": "æ", "√©": "é",
        "√†": "Æ", "√Ö": "Ø", "√Å": "Å", "√É": "É",
        "√™": "™", "√ü": "ü", "√ß": "ß", "√ä": "ä",
        "√¨": "¨", "√à": "à", "√ç": "ç", "√è": "è",
        "√¬": "¬", "√º": "º", "√Ω": "Ω", "√≥": "≥",
        "√≤": "≤", "√∞": "∞", "√∑": "∑",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text

# Function to clean text
def clean_text(text):
    for phrase in noise_phrases:
        text = re.sub(rf"\b{re.escape(phrase)}\b", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# Function to extract title and description from a single PDF
def extract_title_and_description(pdf_path):
    doc = fitz.open(pdf_path)
    blocks = []

    for page in doc:
        page_blocks = page.get_text("dict")["blocks"]
        blocks.extend(page_blocks)

    blocks = sorted(blocks, key=lambda b: b["bbox"][1])  # Top-down sort

    max_font_size = 0
    title_text = None
    description_parts = []

    # Find the title by largest font size
    for block in blocks:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span["text"].strip()
                if not text:
                    continue
                if span["size"] > max_font_size and text not in bad_titles:
                    max_font_size = span["size"]
                    title_text = text

    # After finding the title, start collecting description
    found_title = False
    for block in blocks:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span["text"].strip()
                if not text:
                    continue
                if text == title_text:
                    found_title = True
                    continue
                if found_title and text not in bad_titles:
                    description_parts.append(text)

    full_description = " ".join(description_parts)

    # Clean and fix encoding
    fixed_title = fix_encoding(title_text)
    fixed_description = fix_encoding(full_description)
    fixed_description = clean_text(fixed_description)

    doc.close()
    return fixed_title, fixed_description

# Function to save all jobs to CSV
def save_to_csv(jobs, csv_path):
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "description"])
        for title, description in jobs:
            writer.writerow([title, description])

# --- MAIN ---
jobs = []

for filename in os.listdir(pdf_folder):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder, filename)
        title, description = extract_title_and_description(pdf_path)
        jobs.append((title, description))

save_to_csv(jobs, csv_path)

print(f"✅ Done! Extracted {len(jobs)} job descriptions to {csv_path}.")