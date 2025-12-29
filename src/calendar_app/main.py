#!/usr/bin/env python3
"""
Calendar App - Main Entry Point

UK ILR (Indefinite Leave to Remain) residence day tracking application.
Loads JSON data and displays calendar with trip classifications.

This is the main entry point - equivalent to main() in C programs.
Python uses modules/packages instead of header files.
"""

# Standard library imports (like #include in C, but more flexible)
import tkinter as tk                    # GUI toolkit - like Windows API but cross-platform
from tkinter import messagebox         # Dialog boxes for errors/warnings
import os                              # Operating system interface
import sys                             # Python interpreter interface  
from pathlib import Path               # Modern path handling (better than os.path)

# Local module imports - our own code files
from calendar_app.config import AppConfig           # Configuration management class
from calendar_app.storage.json_loader import DataLoader  # JSON data loading utilities
from calendar_app.ui.grid_layout_manager import GridLayoutManager  # Main 2x2 grid layout coordinator
from calendar_app.model.timeline import DateTimeline          # Date timeline with ILR logic
from calendar_app.model.trips import TripClassifier        # Trip classification system
from calendar_app.model.visaPeriods import VisaClassifier  # Visa period classification system

class CalendarApp:
    """
    Main application class for the ILR Calendar App.
    
    In Python, classes are like structs in C but with methods (functions) attached.
    This class encapsulates all the application state and behavior.
    '__init__' is the constructor (like a constructor in C++)
    'self' is like 'this' pointer - refers to the current instance
    """
    
    def __init__(self):
        """
        Constructor - initializes a new CalendarApp instance.
        Called automatically when you create: app = CalendarApp()
        
        Python doesn't have explicit memory management like C - 
        garbage collector handles allocation/deallocation automatically.
        """
        # Create the main tkinter window - like CreateWindow() in Win32 API
        self.root = tk.Tk()                # 'self.' stores instance variables (like struct members)
        
        # Initialize instance variables to None (like NULL pointers)
        self.config = None                 # Will hold configuration data
        self.data_loader = None            # Will hold data loading object
        self.trips = []                    # Initialize as empty list (prevent AttributeError)
        self.visaPeriods = []             # Initialize as empty list (prevent AttributeError)
        
        # Call initialization methods in sequence
        # (Python allows calling methods from constructor, unlike some C conventions)
        self.setup_window()                # Configure window properties
        self.load_data()                   # Load JSON files
        self.create_widgets()              # Build user interface elements
        
    def setup_window(self):
        """
        Configure the main application window.
        
        This is like setting window properties with SetWindowPos(), etc. in Win32 API
        """
        # Set window title (shown in title bar)
        self.root.title("UK ILR Calendar App")
        
        # Set initial window size to the minimum size to ensure proper layout
        self.root.geometry("900x700")
        
        # Allow window resizing (True = resizable, False = fixed size)
        self.root.resizable(True, True)
        
        # Center the window on screen (like calculating screen coordinates in C)
        self.root.update_idletasks()       # Force tkinter to calculate sizes first
        
        # Get screen dimensions and calculate center position
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = self.root.winfo_reqwidth()
        window_height = self.root.winfo_reqheight()
        
        # Calculate center coordinates (integer division with //)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Set window position: +x+y offset from top-left corner
        self.root.geometry(f"+{x}+{y}")    # f-strings are like sprintf() in C
        
        # Set minimum window size to accommodate the 2x2 grid layout
        # Left column (statistics + info): 350px minimum + Right column (calendar): 500px minimum = 850px
        # Top row (statistics + navigation): 250px + Bottom row (info + calendar): 350px = 600px
        # Add padding and margin space: 850px + 50px = 900px width, 600px + 100px = 700px height
        self.root.minsize(900, 700)
        
    def load_data(self):
        """
        Load configuration and JSON data files.
        
        Python exception handling with try/except is like try/catch in C++
        Unlike C error codes, Python uses exceptions for error handling
        """
        try:
            # Get project root directory using pathlib (modern Python path handling)
            # __file__ is current Python file path, like __FILE__ macro in C
            # parent.parent.parent goes up 3 directories: main.py -> calendar_app -> src -> project_root
            project_root = Path(__file__).parent.parent.parent
            
            # Create configuration object (calls AppConfig.__init__)
            self.config = AppConfig(project_root)
            
            # Print statements go to console (like printf in C)
            print(f"✓ Configuration loaded successfully")
            print(f"  - Objective years: {self.config.objective_years}")
            print(f"  - First entry date: {self.config.first_entry_date}")
            
            # Create data loader object with config for validation
            self.data_loader = DataLoader(project_root, self.config)
            
            # Load data files - this returns a tuple (trips, visaPeriods)
            # Python functions can return multiple values (unlike C)
            trips, visaPeriods = self.data_loader.load_all_data()
            
            print(f"✓ Data loaded successfully")
            print(f"  - {len(trips)} trips loaded")        # len() gets array/list size
            print(f"  - {len(visaPeriods)} visa periods loaded")
            
            # Store data as instance variables for later use
            self.trips = trips
            self.visaPeriods = visaPeriods
            
            # Create trip classifier for day-by-day classifications
            self.trip_classifier = TripClassifier(self.config, trips)
            
            # Create visa classifier for visa period mapping
            self.visaPeriod_classifier = VisaClassifier(self.config, visaPeriods)
            
            # Create date timeline with trip and visa integration
            self.timeline = DateTimeline.from_config(self.config, self.trip_classifier, self.visaPeriod_classifier)
            
            print(f"✓ Timeline initialized with {self.timeline.get_total_days()} days")
            print(f"  - Date range: {self.config.start_year}-{self.config.end_year}")
            
        except Exception as e:
            # Exception handling - 'e' contains the error object
            # str() converts any object to string (like toString())
            error_msg = f"Failed to load data: {str(e)}"
            
            print(f"✗ {error_msg}")
            
            # Ensure root window is ready before showing popup
            self.root.update_idletasks()
            
            # Show error dialog to user (like MessageBox in Win32)
            # Make sure the dialog appears on top and gets focus
            messagebox.showerror("Data Loading Error", error_msg, parent=self.root)
            
            # Re-raise the exception to propagate it up to main() for centralized handling
            raise
            
    def create_widgets(self):
        """
        Create the main UI components using the new modular 2x2 grid layout.
        
        In tkinter, widgets are GUI elements (buttons, labels, etc.)
        Similar to creating controls in Win32 API or MFC
        """
        # Create main container frame with padding
        # Frame is like a panel or container - groups other widgets
        main_frame = tk.Frame(self.root, padx=10, pady=10)  # padx/pady = internal padding
        
        # Pack geometry manager arranges widgets in container
        # pack() is like adding to a vertical or horizontal layout
        main_frame.pack(fill=tk.BOTH, expand=True)  # fill entire window, expand when resized
        
        # Grid layout manager - handles the 2x2 layout with ILR statistics and calendar
        # Now uses the new modular architecture with self-contained modules
        self.grid_layout = GridLayoutManager(
            main_frame, 
            config=self.config, 
            timeline=self.timeline
        )
        
        # Pack the grid layout to fill the entire main frame
        self.grid_layout.pack(fill=tk.BOTH, expand=True)
        
    def day_clicked(self, clicked_date):
        """
        Handle when user clicks on a calendar day.
        
        Args:
            clicked_date: The date that was clicked
        """
        # For now, just show basic information
        # Later this will show trip details, visa periods, etc.
        date_str = clicked_date.strftime('%A, %d %B %Y')
        print(f"Calendar day clicked: {date_str}")
        
        # TODO: In next phase, show day details popup with trip information
        
    def run(self):
        """
        Start the application main loop.
        
        This is like the message loop in Win32 programs - processes GUI events
        The method blocks (doesn't return) until user closes the window
        """
        print("Starting Calendar App...")
        
        # Enter tkinter event loop - similar to GetMessage()/DispatchMessage() in Win32
        # This handles button clicks, window resize, etc.
        self.root.mainloop()

def main():
    """
    Application entry point - like int main() in C programs.
    
    Python convention is to have a main() function that starts everything
    """
    app = None  # Initialize app variable for cleanup
    
    try:
        # Create application instance and run it
        app = CalendarApp()           # calls CalendarApp.__init__()
        app.run()                     # starts GUI event loop
        
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully (like signal handling in C)
        print("\\nApplication terminated by user")
        
    except Exception as e:        
        # If we don't have an app instance yet, show a basic error
        print(f"\\nFATAL ERROR: Application failed to start")
        print(f"Error details: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Try to show GUI error dialog if possible
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            messagebox.showerror("Application Error", f"Application failed to start:\\n\\n{str(e)}")
            root.destroy()
        except:
            pass  # If GUI error dialog fails, we already printed to console
    
    finally:
        # Centralized cleanup - finally block (not method) handles shutdown
        if app and hasattr(app, 'root') and app.root:
            print("Application shutting down...")
            try:
                app.root.quit()      # Stop the main loop
                app.root.destroy()   # Destroy the window
            except:
                pass  # Ignore cleanup errors
                
        print("Goodbye!")

# Python equivalent of #ifdef MAIN in C
# Only run main() if this file is executed directly (not imported as module)
if __name__ == "__main__":
    main()