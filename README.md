# PDF Splitter by Index

This project provides a Python script that splits a PDF into multiple files based on a TSV (tab-separated) index.  
It handles **roman numeral** pages (for front matter) and **numeric** pages (for chapters), calculates the offset from the actual PDF page numbers, and creates individual PDFs accordingly.

---

## Features

1. **Parse a TSV index** that includes titles and page references (in roman numerals or decimal).
2. **Prompt the user** for the actual PDF page corresponding to the first numbered chapter.
3. **Automatically adjust** all subsequent page numbers based on the offset.
4. **Split the PDF** accordingly, creating separate PDF files named with a leading-zero counter to keep them in alphabetical order.

---

## Setup & Installation

We recommend using a **virtual environment** to keep dependencies isolated.

### 1. Clone or Download the Repository

```bash
git clone https://github.com/racoci/pdf-splitter.git
cd pdf-index-splitter
```

*(Alternatively, just download the script and the two files here: `split_pdf_by_index.py`, `requirements.txt`, and `README.md`.)*

### 2. Create and Activate a Virtual Environment

#### Windows (Command Prompt):
```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

> **Note:** Ensure you have Python 3 installed. Verify by running:  
> ```bash
> python --version
> ```
> or  
> ```bash
> python3 --version
> ```

### 3. Install Dependencies

Inside the activated virtual environment, install the required libraries using:

```bash
pip install -r requirements.txt
```

This will install [**PyPDF2**](https://pypi.org/project/PyPDF2/) (and any other listed libraries).

---

## Usage

1. **Make the script executable** (optional on Windows) by modifying permissions on macOS/Linux:
   ```bash
   chmod +x split_pdf_by_index.py
   ```

2. **Run the Script** with your PDF file path as an argument:
   ```bash
   python split_pdf_by_index.py /path/to/mybook.pdf
   ```
   
3. **Paste your TSV Index** when prompted:

   ```
   PDF File Name  PDF Page
   Prefácio       xiii
   Introdução     1
   Capítulo 1 - Algumas Lógicas Paraconsistentes    19
   Capítulo 2 - Paraconsistência e Conjuntos        35
   ...
   ```

   Then press **Enter** and **Ctrl+D** (Linux/Mac) or **Ctrl+Z** (Windows) to finish reading input.

4. **Provide the actual PDF page** when asked about the first numbered entry (for example, if the script indicates `Introdução` is listed at page `1` in the index, but in your PDF viewer it appears at page `5`, you type `5`).

5. The script will **adjust** the page numbers and **split** the PDF, writing multiple smaller PDFs in the same directory:
   - `./01 Prefácio.pdf`
   - `./02 Introdução.pdf`
   - `./03 Capítulo 1 - Algumas Lógicas Paraconsistentes.pdf`
   - etc.

---

## Example

### Example Command

```bash
python split_pdf_by_index.py sample.pdf
```

### Example TSV

```text
PDF File Name    PDF Page
Prefácio         xiii
Introdução       1
Capítulo 1 - Algumas Lógicas Paraconsistentes    19
Capítulo 2 - Paraconsistência e Conjuntos        35
```

### Example Prompt in Terminal

```
Please paste your TSV index below. Press Enter when you're done, and then press Ctrl+D (on Linux/Mac) or Ctrl+Z (on Windows) to finish.

PDF File Name    PDF Page
Prefácio         xiii
Introdução       1
Capítulo 1 - Algumas Lógicas Paraconsistentes    19
Capítulo 2 - Paraconsistência e Conjuntos        35

[Press Enter, then Ctrl+D]

The first numbered chapter in your index appears to be 'Introdução' (index page 1).
Please type the actual PDF page number where this chapter starts in the PDF file: 5

Created: 01 Prefácio.pdf (Pages 1–4 in the PDF)
Created: 02 Introdução.pdf (Pages 5–18 in the PDF)
Created: 03 Capítulo 1 - Algumas Lógicas Paraconsistentes.pdf (Pages 19–34 in the PDF)
Created: 04 Capítulo 2 - Paraconsistência e Conjuntos.pdf (Pages 35–end in the PDF)

Splitting complete!
Generated files:
  - 01 Prefácio.pdf
  - 02 Introdução.pdf
  - 03 Capítulo 1 - Algumas Lógicas Paraconsistentes.pdf
  - 04 Capítulo 2 - Paraconsistência e Conjuntos.pdf
```

---

## License

*(Include your chosen license here, e.g. MIT, Apache 2.0, etc.)*  

```
MIT License
Copyright (c) 202X ...
Permission is hereby granted, free of charge, ...
```

---

## Contributing

Contributions, feature requests, and bug reports are welcome. Just open an issue or pull request on GitHub!

---

## Support

If you encounter any issues:
1. Check if you have the **latest version** of Python.
2. Ensure you’ve **activated** your virtual environment.
3. Confirm that **PyPDF2** is installed:
   ```bash
   pip show PyPDF2
   ```
4. If problems persist, open an issue or contact the repository owner.

---

Happy Splitting!