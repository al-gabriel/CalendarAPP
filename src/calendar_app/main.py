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
from config import AppConfig           # Configuration management class
from storage.json_loader import DataLoader  # JSON data loading utilities
from ui.calendar_view import CalendarView    # Calendar display widget

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
        self.visa_periods = []             # Initialize as empty list (prevent AttributeError)
        self.calendar_view = None          # Will hold calendar widget
        
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
        
        # Set initial window size: width x height in pixels
        self.root.geometry("800x600")
        
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
        
        # Set minimum window size to prevent calendar distortion
        # Calendar needs minimum space: 7 columns * 90px + navigation + padding ≈ 750px width
        # Header + day headers + 6 weeks + padding ≈ 600px height
        self.root.minsize(750, 600)
        
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
            
            # Create data loader object
            self.data_loader = DataLoader(project_root)
            
            # Load data files - this returns a tuple (trips, visa_periods)
            # Python functions can return multiple values (unlike C)
            trips, visa_periods = self.data_loader.load_all_data()
            
            print(f"✓ Data loaded successfully")
            print(f"  - {len(trips)} trips loaded")        # len() gets array/list size
            print(f"  - {len(visa_periods)} visa periods loaded")
            
            # Store data as instance variables for later use
            self.trips = trips
            self.visa_periods = visa_periods
            
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
        Create the main UI components.
        
        In tkinter, widgets are GUI elements (buttons, labels, etc.)
        Similar to creating controls in Win32 API or MFC
        """
        # Create main container frame with padding
        # Frame is like a panel or container - groups other widgets
        main_frame = tk.Frame(self.root, padx=20, pady=20)  # padx/pady = internal padding
        
        # Pack geometry manager arranges widgets in container
        # pack() is like adding to a vertical or horizontal layout
        main_frame.pack(fill=tk.BOTH, expand=True)  # fill entire window, expand when resized
        
        # Title label widget (like static text control in Win32)
        title_label = tk.Label(
            main_frame,                    # parent widget
            text="UK ILR Calendar App",    # displayed text
            font=("Arial", 18, "bold")     # font tuple: (family, size, style)
        )

        # Position with padding: (top, right, bottom, left) - like CSS
        title_label.pack(pady=(0, 20))    # 0 pixels top, 20 pixels bottom
        
        # Frame for data summary section
        summary_frame = tk.Frame(main_frame)
        summary_frame.pack(fill=tk.X, pady=10)     # fill horizontally, 10px vertical padding
        
        # Build summary text using f-string formatting
        # This is like building a string with sprintf() in C
        summary_text = f"""Data Summary:"""
        summary_text += f"\n• {len(self.trips)} trips loaded"
        summary_text += f"\n• {len(self.visa_periods)} visa periods loaded"
        
        # Add configuration info if available
        if self.config:                    # Check if config loaded successfully (not None)
            summary_text += f"\n• Objective: {self.config.objective_years} years of residence"
            summary_text += f"\n• First entry date: {self.config.first_entry_date}"
            summary_text += f"\n• Target completion: {self.config.target_completion_date.strftime('%d-%m-%Y')}"
        
        # Create label to display summary text
        summary_label = tk.Label(
            summary_frame,
            text=summary_text,
            font=("Arial", 10),            # smaller font than title
            justify=tk.LEFT,               # left-align text
            anchor="w"                     # west anchor (left side)
        )
        summary_label.pack(fill=tk.X)      # fill horizontally
        
        # Status section at bottom
        status_frame = tk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(20, 0))  # 20px top padding, 0 bottom
        
        # Determine status message and color based on loaded data
        status_text = "✓ Application loaded successfully"
        text_color = "green"
        
        # Check if there were loading problems
        if not self.config or len(self.trips) == 0:
            status_text = "⚠ Some data files could not be loaded"
            text_color = "orange"
            
        # Create status label with conditional color
        status_label = tk.Label(
            status_frame,
            text=status_text,
            font=("Arial", 9),
            fg=text_color                  # foreground color (text color)
        )
        status_label.pack()
        
        # Calendar view widget - shows month grid with navigation
        # This is the main calendar display component
        self.calendar_view = CalendarView(main_frame, config=self.config)
        
        # Set up day click callback for future trip detail display
        self.calendar_view.set_day_click_callback(self.day_clicked)
        
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
        
    except Exception:        
        # If we don't have an app instance yet, show a basic error
        pass
    
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