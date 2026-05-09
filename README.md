# PhishGuard AI

[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.x-red)](https://streamlit.io/)
[![OCR](https://img.shields.io/badge/OCR-Tesseract-green)](https://github.com/tesseract-ocr/tesseract)

PhishGuard AI is a defensive, educational phishing detector that analyzes URLs, text messages, screenshots, and PDFs to flag common phishing signals. It combines rule-based heuristics with a lightweight ML baseline to provide a clear risk level and explainable reasons.

## Highlights

- URL analysis with 11+ phishing signals (IP hosts, shorteners, suspicious TLDs, punycode, etc.)
- Text analysis in Spanish and English (urgency, credential requests, financial prompts, brand impersonation)
- Screenshot OCR (in-memory) with Tesseract
- PDF text extraction with optional OCR for scanned documents
- Risk scoring (low/medium/high) with human-readable reasons
- ML baseline (TF-IDF + Logistic Regression) for comparison

## Tech Stack

- Python 3.11+
- Streamlit UI
- OCR: Tesseract + pytesseract
- PDF: pdfplumber + pdf2image
- ML: scikit-learn, pandas, joblib

## Project Structure

- interfaces/app.py: Streamlit UI
- analyzers/: URL, text, OCR, and PDF analyzers
- scoring/: risk scoring and aggregation
- reports/: report generator
- ml/: training script for baseline ML model
- data/: simulated datasets (CSV and JSON)
- models/: saved ML model

## Setup

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
```

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install streamlit validators pytesseract pillow pdfplumber pdf2image scikit-learn pandas joblib
```

### OCR Requirements (Windows)

Install Tesseract and Poppler, then set environment variables:

```powershell
$env:TESSERACT_CMD = "C:\Program Files\Tesseract-OCR\tesseract.exe"
$env:POPPLER_PATH = "C:\Program Files\poppler-24.02.0\Library\bin"
```

## Run the App

```bash
python -m streamlit run interfaces/app.py
```

Open the URL shown in the terminal (default)

## Train the ML Baseline

```bash
python ml/train_baseline.py
```

The model is saved to models/phishguard_baseline.joblib and loaded automatically by the app.

## Dataset

Simulated examples are provided in data/dataset.csv and data/dataset.json. The format includes:

- label: phishing | benign
- url: optional
- text: optional
- language: es | en
- date: YYYY-MM-DD
- source: simulated

## Ethics and Scope

This project is intended for defensive and educational use only. It does not perform exploitation or offensive scanning. The goal is to help users identify common phishing patterns and understand why a message is risky.

## Limitations

- Small simulated dataset; ML baseline is illustrative, not production-grade
- OCR quality depends on image clarity and Tesseract configuration
- Heuristics can produce false positives/negatives

## Roadmap

- Larger labeled dataset with balanced classes
- Improved feature engineering (entropy, typosquatting, domain similarity)
- Model explainability and evaluation dashboards
- Language detection and per-language rules

## License

MIT (add or update as needed)
