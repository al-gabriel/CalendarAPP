"""
PDF Index Module

Handles filename pattern matching to find PDF files for specific flights
based on departure and return dates.
"""

from datetime import date
from typing import Optional, List
from pathlib import Path


class PDFIndex:
    """
    Handles mapping between flight dates and PDF files in the travel_pdfs directory.
    
    Supports various filename patterns and finds matching PDF files for
    outbound and inbound flights.
    """
    
    def __init__(self, pdf_directory: str):
        """
        Initialize PDF index with the travel PDFs directory.
        
        Args:
            pdf_directory: Path to the directory containing travel PDF files
        """
        self.pdf_directory = Path(pdf_directory)
    
    @staticmethod
    def _date_patterns(target_date: date) -> List[str]:
        """Date formats that may appear in a PDF filename."""
        return [
            target_date.strftime("%d-%m-%Y"),  # 15-09-2024
            target_date.strftime("%Y-%m-%d"),  # 2024-09-15
            target_date.strftime("%d%m%Y"),    # 15092024
            target_date.strftime("%Y%m%d"),    # 20240915
            target_date.strftime("%d_%m_%Y"),  # 15_09_2024
            target_date.strftime("%Y_%m_%d"),  # 2024_09_15
        ]
    
    @classmethod
    def _name_has_date(cls, filename: str, target_date: date) -> bool:
        """True if the filename contains target_date in any supported format."""
        return any(pattern in filename for pattern in cls._date_patterns(target_date))
    
    def find_pdfs_for_date(self, target_date: date) -> List[str]:
        """
        Find all PDF files whose filename contains the given date.
        
        Args:
            target_date: Date to search for in PDF filenames
            
        Returns:
            Sorted list of full paths to matching PDF files
        """
        return [pdf for pdf in self.get_all_pdfs()
                if self._name_has_date(Path(pdf).stem.lower(), target_date)]
    
    def find_pdf_for_date(self, target_date: date,
                          companion_date: Optional[date] = None) -> Optional[str]:
        """
        Find the PDF file that best matches the given date.
        
        Searches for PDF files with various date patterns in the filename:
        - dd-mm-yyyy format (e.g., "15-09-2024")
        - yyyy-mm-dd format (e.g., "2024-09-15") 
        - ddmmyyyy format (e.g., "15092024")
        - yyyymmdd format (e.g., "20240915")
        
        When several files contain the date (e.g. one trip's return day is
        another trip's departure day), a file that also contains companion_date
        (the other date of the same trip) is preferred.
        
        Args:
            target_date: Date to search for in PDF filenames
            companion_date: Other date of the same trip, used to break ties
            
        Returns:
            Full path to matching PDF file, or None if not found
        """
        candidates = self.find_pdfs_for_date(target_date)
        if not candidates:
            return None
        
        if companion_date is not None:
            for pdf in candidates:
                if self._name_has_date(Path(pdf).stem.lower(), companion_date):
                    return pdf
        
        return candidates[0]
    
    def find_pdfs_for_trip(self, departure_date: date, return_date: date) -> dict:
        """
        Find PDF files for both outbound and inbound flights of a trip.
        
        Args:
            departure_date: Date of outbound flight
            return_date: Date of inbound flight
            
        Returns:
            Dictionary with 'outbound' and 'inbound' keys containing PDF paths or None
        """
        return {
            'outbound': self.find_pdf_for_date(departure_date, return_date),
            'inbound': self.find_pdf_for_date(return_date, departure_date)
        }
    
    def get_all_pdfs(self) -> List[str]:
        """
        Get list of all PDF files in the travel directory.
        
        Returns:
            Sorted list of full paths to all PDF files
        """
        if not self.pdf_directory.is_dir():
            return []
        
        return sorted(str(pdf.absolute()) for pdf in self.pdf_directory.glob("*.pdf"))
