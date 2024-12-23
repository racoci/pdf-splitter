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
6. Save each split PDF as "./01 Title.pdf", "./02 Title.pdf", etc.
"""

import sys
import re
import PyPDF2

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
    print("Please paste your TSV index below. Press Enter when you're done, and then press Ctrl+D (on Linux/Mac) or Ctrl+Z (on Windows) to finish.\n")
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
    # We assume tab-separated or at least "tsv" means "\t" or consistent whitespace.
    # We'll take the first row as a potential header.
    header = tsv_lines[0].split("\t")
    # Attempt to detect if we have a header (by matching known words).
    if "PDF File Name" in header and "PDF Page" in header:
        # skip the first line
        data_lines = tsv_lines[1:]
    else:
        # no header
        data_lines = tsv_lines

    for line in data_lines:
        parts = line.split("\t")
        # Expect 2 columns: Title, Page
        if len(parts) < 2:
            # skip or handle error
            continue
        title = parts[0].strip()
        page_str = parts[1].strip()

        # Decide if 'page_str' is numeric or roman
        if page_str.isdigit():
            page_num = int(page_str)
        elif looks_like_roman(page_str):
            page_num = roman_to_int(page_str)
        else:
            # fallback: if there's an unknown format
            # you could skip, or handle differently
            print(f"Warning: page '{page_str}' not recognized as numeric or roman. Skipping.")
            continue

        entries.append((title, page_num))

    if not entries:
        print("No valid entries were parsed from TSV. Exiting.")
        sys.exit(1)

    # 3. Identify the first numeric entry in the list.
    #    We'll assume the first numeric entry is just the first that was indeed numeric
    #    (not roman), or the user wants the first that logically should be "page 1".
    #    But in your instructions, we specifically ask the user for the actual PDF page
    #    of the 'first numbered page' (the first numeric entry in the index).
    # 
    #    For example, if the first numeric page in the index is 'Introdução' (page 1),
    #    we want to ask the user: "What is the actual PDF page for 'Introdução'?".
    #    Then we calculate offset = actual_pdf_page - 1.
    #
    #    Implementation detail: We'll find the *first* entry that has a numeric 'page_num'
    #    that matches the smallest among numeric entries. Alternatively, you can do
    #    whichever logic you prefer. Here, we'll search by "the first that is not from a roman".
    
    # We'll pick the first with the smallest "page_num" that isn't obviously Roman from the TSV input.
    # Actually, we've already converted all pages to integers above, so let's do it differently:
    # we want to find the *first numeric page in the original sense*, i.e. typically "1".
    # For safety, let's just pick the smallest integer overall (like 1, 2, 3...) among entries as "first numbered page".
    
    # If you want to be more explicit, you can do:
    # first_numbered_title, first_numbered_index_page = next((t, p) for (t, p) in entries if ... some condition ...)
    # But let's just pick the minimum:
    numeric_entries = [ (t, p) for (t, p) in entries if p > 0 ]
    if not numeric_entries:
        print("No numeric entries found in the TSV. Exiting.")
        sys.exit(1)
    first_numbered_title, first_numbered_index_page = min(numeric_entries, key=lambda x: x[1])

    # 4. Ask the user: "What is the actual PDF page for <first_numbered_title> (index page <first_numbered_index_page>)?"
    print(f"The first numbered chapter in your index appears to be '{first_numbered_title}' (index page {first_numbered_index_page}).")
    user_input = input("Please type the actual PDF page number where this chapter starts in the PDF file: ")
    try:
        actual_pdf_page_for_first_numbered = int(user_input)
    except ValueError:
        print("Invalid page number. Exiting.")
        sys.exit(1)

    # 5. Calculate the offset: 
    #    offset = (actual PDF page) - (indexed page for the first numeric entry)
    offset = actual_pdf_page_for_first_numbered - first_numbered_index_page

    # 6. Adjust all pages (including the roman ones) by adding offset.
    #    We'll re-create a new list: adjusted_entries = [(title, pdf_page), ...]
    adjusted_entries = []
    for (title, index_page) in entries:
        pdf_page_num = index_page + offset
        adjusted_entries.append((title, pdf_page_num))

    # 7. Split the PDF according to these pages.
    #    The idea: if we have N entries, each entry covers a range from its page up to
    #    the page before the next entry. The last entry goes until the end of the PDF.
    #    Note: PyPDF2 uses zero-based page indices. If the user says "the PDF page is 5",
    #    that is page index 4. We must subtract 1 when extracting. 
    #    We'll carefully handle that by using pdf_page_num - 1 for PyPDF2 slicing.
    
    reader = PyPDF2.PdfReader(pdf_path)
    total_pages = len(reader.pages)  # zero-based count of pages

    # Sort the adjusted entries by their actual pdf page
    # (in case the TSV is out of order, though that would be unusual).
    adjusted_entries.sort(key=lambda x: x[1])

    # We'll go entry by entry, taking pages from "this entry's page (0-based)" up to
    # "next entry's page (0-based) - 1".
    splitted_files = []
    for i, (title, start_page) in enumerate(adjusted_entries):
        # If there's a next entry, take one page before it as the end.
        if i < len(adjusted_entries) - 1:
            end_page = adjusted_entries[i+1][1] - 1  # inclusive
        else:
            end_page = total_pages  # all the way to the end (0-based means total_pages - 1, but we'll handle carefully)

        # Safety check: ensure in range
        # Convert to zero-based
        start_0based = start_page - 1
        end_0based = end_page - 1

        if start_0based < 0:
            start_0based = 0
        if end_0based >= total_pages:
            end_0based = total_pages - 1

        if end_0based < start_0based:
            # Something weird, skip
            print(f"Warning: invalid range for '{title}'. Skipping.")
            continue

        # Extract the pages
        writer = PyPDF2.PdfWriter()
        for page_num in range(start_0based, end_0based + 1):
            writer.add_page(reader.pages[page_num])

        # Prepare the output filename
        # We'll use a 2-digit counter with leading zeros: e.g. "01 Title.pdf"
        file_index = i + 1
        filename = f"{file_index:02d} {sanitize_filename(title)}.pdf"

        with open(filename, "wb") as outfile:
            writer.write(outfile)

        splitted_files.append(filename)
        print(f"Created: {filename} (Pages {start_0based+1}–{end_0based+1} in the PDF)")

    print("\nSplitting complete!")
    print("Generated files:")
    for f in splitted_files:
        print("  -", f)

if __name__ == "__main__":
    main()
