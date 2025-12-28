"""
Configuration management for the Calendar App.

Handles loading and validation of config.json file.
This module encapsulates all configuration-related functionality.
"""

# Standard library imports
import json                            # JSON parsing library (like cJSON in C)
from datetime import datetime, timedelta  # Date/time handling
from pathlib import Path               # Modern path manipulation  
from typing import Optional           # Type hints (like declaring types in C headers)

class AppConfig:
    """
    Application configuration loaded from config.json.
    
    This class loads, validates, and provides access to configuration settings.
    Similar to a configuration manager in C applications.
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize configuration from config.json.
        
        Args:
            project_root: Path to the project root directory
            
        The 'project_root: Path' syntax is a type hint - tells you what type to expect
        (optional in Python, but helpful for debugging and IDE support)
        """
        # Store constructor parameters as instance variables
        self.project_root = project_root
        
        # Build path to config.json file 
        # Path / "string" is path joining (like PathCombine in Win32)
        self.config_path = project_root / "data" / "config.json"
        
        # Set default configuration values (like #define constants in C)
        # These will be overridden by values from JSON file
        self.travel_pdf_folder = "../travel_pdfs"
        self.objective_years = 10
        self.processing_buffer_years = 1
        self.start_year = 2023
        self.end_year = 2040
        self.first_entry_date = "29-03-2023"
        
        # Load actual configuration from file
        self.load_config()                 # Parse and validate JSON
        
        # Calculate derived values from loaded config
        self.calculate_derived_values()    # Compute target dates, etc.
        
    def load_config(self):
        """
        Load configuration from config.json file.
        
        Reads JSON file, parses it, and updates instance variables.
        Handles file I/O errors and JSON parsing errors gracefully.
        """
        # Check if file exists before trying to read it
        if not self.config_path.exists():
            # Raise exception (like returning error code in C)
            # f-string formatting inserts variable values into string
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
        try:
            # Open file for reading with UTF-8 encoding
            # 'with' statement ensures file is closed automatically (like RAII in C++)
            with open(self.config_path, 'r', encoding='utf-8') as f:
                # Parse JSON content into Python dictionary (like hash map)
                config_data = json.load(f)
                
            # Update instance variables from JSON data
            # dict.get(key, default) returns value for key, or default if key missing
            # This provides fallback values if JSON is incomplete
            self.travel_pdf_folder = config_data.get("travel_pdf_folder", self.travel_pdf_folder)
            self.objective_years = config_data.get("objective_years", self.objective_years)
            self.processing_buffer_years = config_data.get("processing_buffer_years", self.processing_buffer_years)
            self.start_year = config_data.get("start_year", self.start_year)
            self.end_year = config_data.get("end_year", self.end_year)
            self.first_entry_date = config_data.get("first_entry_date", self.first_entry_date)
            
            # Validate that all values are reasonable
            self.validate_config()
            
        except json.JSONDecodeError as e:
            # Specific exception for JSON parsing errors
            raise ValueError(f"Invalid JSON in config file: {e}")
            
        except Exception as e:
            # Catch-all for other file I/O errors
            raise RuntimeError(f"Failed to load configuration: {e}")
            
    def validate_config(self):
        """
        Validate configuration values.
        
        Checks that all configuration values are reasonable and consistent.
        Raises ValueError if any validation fails.
        """
        # Validate objective_years is a positive integer
        # isinstance() is like checking variable type (similar to typeof in C)
        if not isinstance(self.objective_years, int) or self.objective_years < 5:
            raise ValueError("objective_years must be a positive integer bigger than 5")
            
        # Validate processing_buffer_years is non-negative integer  
        if not isinstance(self.processing_buffer_years, int) or self.processing_buffer_years < 0:
            raise ValueError("processing_buffer_years must be a non-negative integer")
            
        # Validate start_year is reasonable
        if not isinstance(self.start_year, int) or self.start_year < 2000 or self.start_year > 2100:
            raise ValueError("start_year must be a valid year between 2000 and 2100")
            
        # Validate end_year is after start_year and within reasonable bounds
        if not isinstance(self.end_year, int) or self.end_year <= self.start_year or self.end_year > 2100:
            raise ValueError("end_year must be greater than start_year and no later than 2100")
            
        # Validate and parse first_entry_date format
        try:
            # strptime parses date string according to format (like strptime in C)
            # %d = day, %m = month, %Y = 4-digit year (European format DD-MM-YYYY)
            self.first_entry_date_obj = datetime.strptime(self.first_entry_date, "%d-%m-%Y").date()
            
        except ValueError:
            raise ValueError("first_entry_date must be in DD-MM-YYYY format")
            
        # Validate date is within the configured year range
        start_date = datetime(self.start_year, 1, 1).date()  # January 1st of start year
        end_date = datetime(self.end_year, 12, 31).date()    # December 31st of end year
        
        # Check if first_entry_date is within valid range
        if not (start_date <= self.first_entry_date_obj <= end_date):
            raise ValueError(f"first_entry_date must be between {start_date} and {end_date}")
            
    def calculate_derived_values(self):
        """
        Calculate derived configuration values.
        
        Computes target dates and other calculated values from base configuration.
        This is like calculating constants from #define values in C.
        """
        # Calculate target completion date
        # Add exactly objective_years worth of days to first_entry_date
        # timedelta represents a duration (like adding seconds to time_t in C)
        # This automatically handles leap years through Python's date arithmetic
        days_to_add = timedelta(days=self.objective_years * 365)
        self.target_completion_date = self.first_entry_date_obj + days_to_add
        
        # Calculate exact number of days from start to target
        # This accounts for leap years automatically
        date_diff = self.target_completion_date - self.first_entry_date_obj
        self.ilr_target_days = date_diff.days
        
        # Calculate planning horizon (includes processing buffer)
        buffer_days = timedelta(days=(self.objective_years + self.processing_buffer_years) * 365)
        self.planning_completion_date = self.first_entry_date_obj + buffer_days
        
        # Resolve travel PDF folder path
        # Handle both absolute paths and relative paths
        travel_path = Path(self.travel_pdf_folder)
        
        if travel_path.is_absolute():
            # Path is already absolute (like C:\Users\...)
            self.travel_pdf_path = travel_path
        else:
            # Path is relative (like ../travel_pdfs), make it absolute
            self.travel_pdf_path = self.project_root / self.travel_pdf_folder
            
    def get_summary(self) -> str:
        """
        Get a human-readable summary of the configuration.
        
        Returns:
            Multi-line string with configuration details
            
        The '-> str' is a return type hint (optional but helpful)
        """
        # Build string with explicit newlines 
        summary = "Configuration Summary:"
        summary += f"\n• Objective: {self.objective_years} years of residence"
        summary += f"\n• Processing buffer: {self.processing_buffer_years} years"
        summary += f"\n• Timeline: {self.start_year}-{self.end_year}"
        summary += f"\n• First entry: {self.first_entry_date}"
        summary += f"\n• Target completion: {self.target_completion_date.strftime('%d-%m-%Y')}"
        summary += f"\n• ILR target days: {self.ilr_target_days}"
        summary += f"\n• Travel PDFs: {self.travel_pdf_path}"
        return summary

    def __repr__(self) -> str:
        """
        String representation for debugging.
        
        __repr__ is a special method (like toString() in Java)
        Called when you print() the object or use it in debugging
        """
        return f"AppConfig(objective_years={self.objective_years}, first_entry_date='{self.first_entry_date}')"