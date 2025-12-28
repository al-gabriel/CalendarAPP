"""
JSON data loading utilities.

Handles loading and validation of trips.json and visaPeriods.json files.
"""

import json
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from calendar_app.config import AppConfig

class DataLoader:
    """Loads and validates JSON data files."""
    
    def __init__(self, project_root: Path, config: AppConfig):
        """
        Initialize data loader.
        
        Args:
            project_root: Path to the project root directory
            config: Application configuration (required for validation)
        """
        self.project_root = project_root
        self.data_path = project_root / "data"
        self.config = config
        
    def load_json_file(self, filename: str) -> List[Dict[str, Any]]:
        """
        Load and validate a JSON file.
        
        Args:
            filename: Name of the JSON file to load
            
        Returns:
            Parsed JSON data as list of dictionaries
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If JSON is invalid
        """
        file_path = self.data_path / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Ensure data is a list
            if not isinstance(data, list):
                raise ValueError(f"{filename} must contain a JSON array")
                
            return data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {filename}: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load {filename}: {e}")
            
    def validate_trip(self, trip: Dict[str, Any], first_entry_date: date) -> Dict[str, Any]:
        """
        Validate a single trip record.
        
        Args:
            trip: Trip dictionary to validate
            first_entry_date: First UK entry date for validation (as date object)
            
        Returns:
            Validated trip dictionary with parsed dates
            
        Raises:
            ValueError: If trip data is invalid
        """
        required_fields = ["id", "departure_date", "return_date", "from_airport", "to_airport"]
        
        # Check required fields
        for field in required_fields:
            if field not in trip:
                raise ValueError(f"Trip missing required field: {field}")
                
        # Validate and parse dates
        try:
            departure_date = datetime.strptime(trip["departure_date"], "%d-%m-%Y").date()
            return_date = datetime.strptime(trip["return_date"], "%d-%m-%Y").date()
        except ValueError as e:
            raise ValueError(f"Invalid date format in trip {trip.get('id', 'unknown')}: {e}")
            
        # Validate date logic
        if return_date < departure_date:
            raise ValueError(f"Trip {trip['id']}: return_date must be >= departure_date")
                # CRITICAL VALIDATION: No trips before first UK entry  
        if departure_date < first_entry_date:
            raise ValueError(
                f"Trip {trip['id']}: departure_date ({departure_date.strftime('%d-%m-%Y')}) "
                f"is before first UK entry date ({first_entry_date.strftime('%d-%m-%Y')}). "
                f"Trips cannot exist before first UK entry."
            )
            
        # Calculate trip length
        trip_length = (return_date - departure_date).days + 1
        
        # Create validated trip with parsed dates and calculated values
        validated_trip = trip.copy()
        validated_trip["departure_date_obj"] = departure_date
        validated_trip["return_date_obj"] = return_date
        validated_trip["trip_length_days"] = trip_length
        validated_trip["is_short_trip"] = trip_length < 14
        
        return validated_trip
        
    def validate_visaPeriod(self, visa: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a single visa period record.
        
        Args:
            visa: Visa period dictionary to validate
            
        Returns:
            Validated visa period dictionary with parsed dates
            
        Raises:
            ValueError: If visa period data is invalid
        """
        required_fields = ["id", "label", "start_date", "end_date"]
        
        # Check required fields
        for field in required_fields:
            if field not in visa:
                raise ValueError(f"Visa period missing required field: {field}")
                
        # Validate and parse dates
        try:
            start_date = datetime.strptime(visa["start_date"], "%d-%m-%Y").date()
            end_date = datetime.strptime(visa["end_date"], "%d-%m-%Y").date()
        except ValueError as e:
            raise ValueError(f"Invalid date format in visa period {visa.get('id', 'unknown')}: {e}")
            
        # Validate date logic
        if end_date < start_date:
            raise ValueError(f"Visa period {visa['id']}: end_date must be >= start_date")
            
        # BUSINESS RULE: Visa periods must be within the defined timeline range
        timeline_start_date = datetime(self.config.start_year, 1, 1).date()
        timeline_end_date = datetime(self.config.end_year, 12, 31).date()
        
        if start_date < timeline_start_date:
            raise ValueError(
                f"Visa period {visa['id']}: start_date ({start_date.strftime('%d-%m-%Y')}) "
                f"is before timeline start date ({timeline_start_date.strftime('%d-%m-%Y')}). "
                f"Visa periods must be within the defined timeline range."
            )
            
        if end_date > timeline_end_date:
            raise ValueError(
                f"Visa period {visa['id']}: end_date ({end_date.strftime('%d-%m-%Y')}) "
                f"is beyond timeline end date ({timeline_end_date.strftime('%d-%m-%Y')}). "
                f"Visa periods must be within the defined timeline range."
            )
            
        # Create validated visa period with parsed dates
        validated_visa = visa.copy()
        validated_visa["start_date_obj"] = start_date
        validated_visa["end_date_obj"] = end_date
        validated_visa["duration_days"] = (end_date - start_date).days + 1
        
        return validated_visa
        
    def load_trips(self) -> List[Dict[str, Any]]:
        """
        Load and validate all trips from trips.json.
        
        Returns:
            List of validated trip dictionaries
            
        Raises:
            ValueError: If any trip data is invalid
        """
        trips_data = self.load_json_file("trips.json")
        validated_trips = []
        
        # Get first_entry_date from config (use the parsed date object)
        first_entry_date = self.config.first_entry_date_obj
        
        for i, trip in enumerate(trips_data):
            try:
                validated_trip = self.validate_trip(trip, first_entry_date)
                validated_trips.append(validated_trip)
            except ValueError as e:
                # Raise exception instead of just warning - this will trigger the error popup
                raise ValueError(f"Invalid trip at index {i}: {e}")
                
        return validated_trips
            
    def load_visaPeriods(self) -> List[Dict[str, Any]]:
        """
        Load and validate all visa periods from visaPeriods.json.
        
        Returns:
            List of validated visa period dictionaries
            
        Raises:
            ValueError: If any visa period data is invalid
        """
        visaPeriods_data = self.load_json_file("visaPeriods.json")
        validated_visas = []
        
        for i, visa in enumerate(visaPeriods_data):
            try:
                validated_visa = self.validate_visaPeriod(visa)
                validated_visas.append(validated_visa)
            except ValueError as e:
                # Raise exception instead of just warning - this will trigger the error popup
                raise ValueError(f"Invalid visa period at index {i}: {e}")
                
        return validated_visas
            
    def load_all_data(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Load all data files.
        
        Returns:
            Tuple of (trips, visaPeriods)
        """
        trips = self.load_trips()
        visaPeriods = self.load_visaPeriods()
        
        return trips, visaPeriods
        
    def get_data_summary(self, trips: List[Dict[str, Any]], visaPeriods: List[Dict[str, Any]]) -> str:
        """
        Generate a summary string of loaded data.
        
        Args:
            trips: List of trip dictionaries
            visaPeriods: List of visa period dictionaries
            
        Returns:
            Human-readable summary string
        """
        short_trips = sum(1 for trip in trips if trip.get("is_short_trip", False))
        long_trips = len(trips) - short_trips
        
        total_trip_days = sum(trip.get("trip_length_days", 0) for trip in trips)
        
        # Build summary text using f-string formatting (same pattern as main.py)
        summary_text = f"""Data Summary:"""
        summary_text += f"\n• {len(trips)} trips total ({short_trips} short, {long_trips} long)"
        summary_text += f"\n• {total_trip_days} total trip days"
        summary_text += f"\n• {len(visaPeriods)} visa periods"
        summary_text += f"\n• Date range: {min(trip['departure_date'] for trip in trips) if trips else 'N/A'} to {max(trip['return_date'] for trip in trips) if trips else 'N/A'}"
        
        return summary_text