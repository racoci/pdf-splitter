#!/usr/bin/env python3
"""
split_pdf_by_index.py

Usage:
  python split_pdf_by_index.py /path/to/mybook.pdf

This script will:
1. Ask the user for the TSV index.
2. Parse it, converting roman numeral pages to integers where needed.
3. Ask the user for the actual PDF page of the first numeric entry.
4. Compute the offset for all numeric/roman pages in the index.
5. Split the PDF into multiple PDFs based on those page ranges.
6. Save each split PDF into a ./splits/ folder alongside the original PDF.
"""

import sys
import os
import re
import PyPDF2

TSV_INPUT = """

Please paste your TSV index like the one below:

```tsv
PDF File Name	Página
Prefácio	xiii
Introdução	1
Capítulo 1 - Algumas Lógicas Paraconsistentes	19
Capítulo 2 - Paraconsistência e Conjuntos	35
Capítulo 3 - Esboço de Duas Aplicações: Teoria Paraconsistente de Modelos e Cálculo Infinitesimal Paraconsistente	77
A Lógica Paraconsistente: História de uma Revolução Conceitual	99
Paraconsistência: Esboço de uma Interpretação	113
A Lógica Pode Ser Simples (Lógica, Congruência e Álgebra)	151
```

You don't need to add the markdown tags, just paste the tsv directly and them...

Press Enter when you're done, and then press Ctrl+D (on Linux/Mac) or Ctrl+Z (on Windows) to finish.\n
"""

# -- Helpers --

def roman_to_int(roman: str) -> int:
    """
    Convert a (modern) roman numeral string to an integer.
    Example: 'xiii' -> 13, 'iv' -> 4.
    This is a simplified approach assuming well-formed Roman numerals.
    """
    roman = roman.lower()
    roman_map = {
        'm': 1000, 'd': 500, 'c': 100, 'l': 50,
        'x': 10, 'v': 5, 'i': 1
    }
    result = 0
    prev_value = 0
    for char in reversed(roman):
        value = roman_map[char]
        if value >= prev_value:
            result += value
        else:
            result -= value
        prev_value = value
    return result

def looks_like_roman(s: str) -> bool:
    """
    Check if the string s looks like a roman numeral.
    For simplicity, we test if all chars are in the set {i, v, x, l, c, d, m}
    """
    return bool(re.match(r'^[IVXLCDMivxlcdm]+$', s.strip()))

def sanitize_filename(filename: str) -> str:
    """
    Remove or replace characters that might cause issues in file names.
    You can customize as needed.
    """
    # For example, replace slashes, colons, question marks, etc.
    return re.sub(r'[\\/:*?"<>|]', '_', filename)

# -- Main Logic --

def main():
    if len(sys.argv) != 2:
        print("Usage: python split_pdf_by_index.py /path/to/mybook.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]

    # 1. Ask the user to input the TSV.
    print(TSV_INPUT)
    # We'll read from sys.stdin until EOF.
    tsv_lines = sys.stdin.read().strip().splitlines()

    if not tsv_lines:
        print("No TSV data provided. Exiting.")
        sys.exit(1)

    # 2. Parse the TSV lines.
    # Expected format (example):
    # PDF File Name    PDF Page
    # Prefácio         xiii
    # Introdução       1
    # ...
    # We'll skip the header if the first line looks like it.
    entries = []
    header = tsv_lines[0].split("\t")
    if "PDF File Name" in header and "PDF Page" in header:
        # skip the first line
        data_lines = tsv_lines[1:]
    else:
        data_lines = tsv_lines

    for line in data_lines:
        parts = line.split("\t")
        # Expect 2 columns: Title, Page
        if len(parts) < 2:
            # Not enough columns, skip or handle error
            continue

        title = parts[0].strip()
        page_str = parts[1].strip()

        # Decide if 'page_str' is numeric or roman
        if page_str.isdigit():
            page_num = int(page_str)
        elif looks_like_roman(page_str):
            page_num = roman_to_int(page_str)
        else:
            print(f"Warning: page '{page_str}' not recognized as numeric or roman. Skipping.")
            continue

        entries.append((title, page_num))

    if not entries:
        print("No valid entries were parsed from TSV. Exiting.")
        sys.exit(1)

    # 3. Find the first numeric entry in the list (smallest page_num > 0).
    numeric_entries = [(t, p) for (t, p) in entries if p > 0]
    if not numeric_entries:
        print("No numeric entries found in the TSV. Exiting.")
        sys.exit(1)
    first_numbered_title, first_numbered_index_page = min(numeric_entries, key=lambda x: x[1])

    # 4. Ask user for the actual PDF page corresponding to that index page.
    print(f"The first numbered chapter in your index appears to be '{first_numbered_title}' (index page {first_numbered_index_page}).")
    user_input = input("Please type the actual PDF page number where this chapter starts in the PDF file: ")
    try:
        actual_pdf_page_for_first_numbered = int(user_input)
    except ValueError:
        print("Invalid page number. Exiting.")
        sys.exit(1)

    # 5. Calculate the offset
    offset = actual_pdf_page_for_first_numbered - first_numbered_index_page

    # 6. Adjust all pages by the offset
    adjusted_entries = []
    for (title, index_page) in entries:
        pdf_page_num = index_page + offset
        adjusted_entries.append((title, pdf_page_num))

    # 7. Split the PDF according to these pages.
    reader = PyPDF2.PdfReader(pdf_path)
    total_pages = len(reader.pages)  # zero-based count of pages

    # Sort the entries by their new PDF page (just in case).
    adjusted_entries.sort(key=lambda x: x[1])

    # Prepare output folder: "splits" in the same directory as the original PDF
    pdf_dir = os.path.dirname(os.path.abspath(pdf_path))
    split_dir = os.path.join(pdf_dir, "splits")
    os.makedirs(split_dir, exist_ok=True)

    splitted_files = []
    for i, (title, start_page) in enumerate(adjusted_entries):
        if i < len(adjusted_entries) - 1:
            end_page = adjusted_entries[i+1][1] - 1  # inclusive
        else:
            end_page = total_pages  # goes till the end

        # Convert to zero-based for PyPDF2
        start_0based = start_page - 1
        end_0based = end_page - 1

        # Ensure within valid range
        if start_0based < 0:
            start_0based = 0
        if end_0based >= total_pages:
            end_0based = total_pages - 1

        if end_0based < start_0based:
            print(f"Warning: invalid page range for '{title}'. Skipping.")
            continue

        # Extract pages
        writer = PyPDF2.PdfWriter()
        for page_num in range(start_0based, end_0based + 1):
            writer.add_page(reader.pages[page_num])

        # Build output filename in "splits" directory
        file_index = i + 1
        output_filename = f"{file_index:02d} {sanitize_filename(title)}.pdf"
        output_path = os.path.join(split_dir, output_filename)

        with open(output_path, "wb") as outfile:
            writer.write(outfile)

        splitted_files.append(output_path)
        print(f"Created: {output_path} (Pages {start_0based+1}–{end_0based+1} in the PDF)")

    print("\nSplitting complete!")
    print("Generated files:")
    for f in splitted_files:
        print("  -", f)

if __name__ == "__main__":
    main()
