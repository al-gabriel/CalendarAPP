"""
Test Suite for pdf_index.py
Tests PDFIndex filename matching using a temporary folder of empty PDF files.
"""

import sys
import tempfile
from pathlib import Path
from datetime import date

# Add the src directory to Python path to import our modules
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from calendar_app.storage.pdf_index import PDFIndex


SAMPLE_FILES = [
    "LGW_LIS_05-11-2023_19-11-2023.pdf",   # Return trip in one PDF
    "LGW_LIS_13-05-2024.pdf",              # One-way outbound
    "LIS_LGW_20-05-2024.pdf",              # One-way inbound
    "BOH_FAO_20-05-2024_27-05-2024.pdf",   # Shares 20-05-2024 with the file above
    "notes.txt",                           # Not a PDF - must be ignored
]


def make_pdf_dir() -> tempfile.TemporaryDirectory:
    """Create a temp folder containing the sample files."""
    tmp = tempfile.TemporaryDirectory()
    for name in SAMPLE_FILES:
        (Path(tmp.name) / name).touch()
    return tmp


def test_find_pdf_for_single_date():
    """A date found in exactly one filename returns that file."""
    print("Testing single-date match...")
    with make_pdf_dir() as tmp:
        index = PDFIndex(tmp)
        assert Path(index.find_pdf_for_date(date(2024, 5, 13))).name == "LGW_LIS_13-05-2024.pdf"
        assert index.find_pdf_for_date(date(2030, 1, 1)) is None
    print("✓ Single-date match works")


def test_return_trip_pdf_matches_both_dates():
    """Outbound and inbound dates of a return-trip PDF resolve to the same file."""
    print("Testing return-trip PDF...")
    with make_pdf_dir() as tmp:
        index = PDFIndex(tmp)
        pdfs = index.find_pdfs_for_trip(date(2023, 11, 5), date(2023, 11, 19))
        assert Path(pdfs['outbound']).name == "LGW_LIS_05-11-2023_19-11-2023.pdf"
        assert Path(pdfs['inbound']).name == "LGW_LIS_05-11-2023_19-11-2023.pdf"
    print("✓ Return-trip PDF found for both dates")


def test_shared_date_prefers_companion_date():
    """When two PDFs share a date, the one containing the trip's other date wins."""
    print("Testing shared-date tie-break...")
    with make_pdf_dir() as tmp:
        index = PDFIndex(tmp)
        shared = date(2024, 5, 20)
        assert len(index.find_pdfs_for_date(shared)) == 2
        
        # Return of the LIS trip (departed 13-05-2024)
        lis = index.find_pdf_for_date(shared, companion_date=date(2024, 5, 13))
        # Departure of the FAO trip (returns 27-05-2024)
        fao = index.find_pdf_for_date(shared, companion_date=date(2024, 5, 27))
        
        assert Path(fao).name == "BOH_FAO_20-05-2024_27-05-2024.pdf"
        # No file contains both 13-05 and 20-05, so the sorted first match is returned
        assert Path(lis).name == sorted(Path(p).name for p in index.find_pdfs_for_date(shared))[0]
    print("✓ Shared date resolved by companion date")


def test_get_all_pdfs_ignores_other_files():
    """Only .pdf files are listed, in sorted order."""
    print("Testing PDF listing...")
    with make_pdf_dir() as tmp:
        pdfs = PDFIndex(tmp).get_all_pdfs()
        assert len(pdfs) == 4
        assert pdfs == sorted(pdfs)
        assert all(p.endswith(".pdf") for p in pdfs)
    print("✓ Only PDF files listed")


def test_missing_directory():
    """A missing folder returns no matches instead of raising."""
    print("Testing missing directory...")
    index = PDFIndex(str(Path(tempfile.gettempdir()) / "calendar_app_no_such_dir"))
    assert index.get_all_pdfs() == []
    assert index.find_pdf_for_date(date(2024, 5, 13)) is None
    print("✓ Missing directory handled")


def run_all_pdf_index_tests():
    """Run all PDFIndex tests."""
    print("Starting PDFIndex Test Suite...")
    print("=" * 50)
    
    test_find_pdf_for_single_date()
    test_return_trip_pdf_matches_both_dates()
    test_shared_date_prefers_companion_date()
    test_get_all_pdfs_ignores_other_files()
    test_missing_directory()
    
    print("=" * 50)
    print("All PDFIndex tests passed!")


if __name__ == "__main__":
    run_all_pdf_index_tests()
