import cv2
try:
    import customtkinter as ctk
except ImportError:
    import os
    os.system('pip install customtkinter')
    import customtkinter as ctk

from tkinter import Canvas, TclError
from PIL import Image, ImageTk
from uco_reader import YOLOReader
from db_reader import get_document_by_value, get_document_by_name
from ocr import get_medicine_data
import serial
import threading
import time
import os
import tempfile
import math

# Set appearance mode and color theme
ctk.set_appearance_mode("light")

class FieldAnimator:
    """Professional field animation system"""
    
    @staticmethod
    def slide_in_field(widget, delay=0, duration=400):
        """Smooth slide-in animation for individual fields"""
        original_x = widget.winfo_x()
        start_x = original_x - 300
        
        def animate_slide(step=0):
            if step <= duration:
                progress = step / duration
                # Smooth easing function
                eased_progress = 1 - math.pow(1 - progress, 3)
                current_x = start_x + (original_x - start_x) * eased_progress
                
                widget.place(x=int(current_x), y=widget.winfo_y())
                widget.after(16, lambda: animate_slide(step + 16))
            else:
                widget.place_forget()
                widget.pack(fill="x", pady=6)
        
        if delay > 0:
            widget.after(delay, lambda: animate_slide())
        else:
            animate_slide()
    
    @staticmethod
    def value_change_flash(widget, new_text, color="#e8f5e8"):
        """Subtle flash animation when values change"""
        original_color = widget.cget("fg_color")
        
        # Flash effect
        widget.configure(fg_color=color)
        
        def restore_color():
            widget.configure(fg_color=original_color)
        
        widget.after(200, restore_color)

class ProfessionalLoadingIndicator:
    """Elegant loading indicator for processing states"""
    
    def __init__(self, parent, size=30):
        self.parent = parent
        self.size = size
        self.angle = 0
        self.is_active = False
        
        self.canvas = Canvas(
            parent,
            width=size,
            height=size,
            bg='#ffffff',
            highlightthickness=0
        )
        
    def start(self):
        self.is_active = True
        self.canvas.place(relx=0.5, rely=0.5, anchor="center")
        self.animate()
        
    def stop(self):
        self.is_active = False
        self.canvas.place_forget()
        
    def animate(self):
        if self.is_active:
            self.canvas.delete("indicator")
            
            center = self.size // 2
            radius = self.size // 3
            
            # Professional circular indicator
            for i in range(12):
                angle = self.angle + i * 30
                x1 = center + radius * 0.8 * math.cos(math.radians(angle))
                y1 = center + radius * 0.8 * math.sin(math.radians(angle))
                x2 = center + radius * math.cos(math.radians(angle))
                y2 = center + radius * math.sin(math.radians(angle))
                
                alpha = max(0.15, 1.0 - i * 0.08)
                color_val = int(66 + alpha * 120)
                
                self.canvas.create_line(
                    x1, y1, x2, y2,
                    fill=f"#{color_val:02x}{color_val:02x}{color_val:02x}",
                    width=2, capstyle="round", tags="indicator"
                )
            
            self.angle += 10
            self.parent.after(50, self.animate)

class DetectionVisualizer:
    """Professional detection visualization"""
    
    def __init__(self, canvas):
        self.canvas = canvas
        self.detection_active = False
        self.scan_y = 0
        self.scan_direction = 1
        
    def start_detection(self):
        self.detection_active = True
        self.animate_detection()
        
    def stop_detection(self):
        self.detection_active = False
        self.canvas.delete("detection")
        
    def animate_detection(self):
        if not self.detection_active:
            return
            
        self.canvas.delete("detection")
        
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width > 1 and height > 1:
            # Professional scanning beam
            beam_height = 3
            self.scan_y += self.scan_direction * 2
            
            if self.scan_y >= height - beam_height:
                self.scan_direction = -1
            elif self.scan_y <= 0:
                self.scan_direction = 1
            
            # Create gradient scanning beam
            for i in range(beam_height):
                y = self.scan_y + i
                if 0 <= y < height:
                    alpha = 1.0 - (i / beam_height)
                    color_val = int(45 + alpha * 100)
                    self.canvas.create_line(
                        0, y, width, y,
                        fill=f"#{color_val:02x}{int(150 + alpha * 105):02x}{color_val:02x}",
                        width=1, tags="detection"
                    )
            
            # Detection grid overlay
            grid_spacing = 50
            for x in range(0, width, grid_spacing):
                alpha = 0.3
                color_val = int(200 + alpha * 55)
                self.canvas.create_line(
                    x, 0, x, height,
                    fill=f"#{color_val:02x}{color_val:02x}{int(color_val + 20):02x}",
                    width=1, tags="detection"
                )
            
            for y in range(0, height, grid_spacing):
                alpha = 0.3
                color_val = int(200 + alpha * 55)
                self.canvas.create_line(
                    0, y, width, y,
                    fill=f"#{color_val:02x}{color_val:02x}{int(color_val + 20):02x}",
                    width=1, tags="detection"
                )
        
        self.canvas.after(40, self.animate_detection)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title("Professional Medicine Validation System")
        self.geometry("1400x900")
        self.configure(fg_color="#f8f9fa")
        
        # Professional color scheme
        self.colors = {
            'background': '#f8f9fa',
            'card_bg': '#ffffff',
            'text_primary': '#1a1a1a',
            'text_secondary': '#6c757d',
            'success': '#28a745',
            'error': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'border': '#e9ecef',
            'shadow': '#00000010',
            'accent': '#007bff'
        }
        
        # State variables
        self.processing = False
        self.current_step = ""
        self.captured_frame = None
        self.current_frame = None
        self.detection_in_progress = False
        
        # YOLO reader - change cam_index to your camera device ID
        self.camera_index = 2  # Change this value to your camera device ID
        self.reader = YOLOReader(model_path="best.pt", cam_index=self.camera_index, conf=0.7)
        
        # Setup UI
        self.setup_ui()
        
        # Start video loop
        self.update_video()
        
        # Serial setup
        self.setup_serial()
        
        # Escape key to exit fullscreen
        self.bind("<Escape>", lambda e: self.destroy())
        
        # Closing hook
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        # Configure grid weights
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        
        # Create main panels
        self.create_video_panel()
        self.create_analysis_panel()
        self.create_status_bar()
        
    def create_video_panel(self):
        # Video panel with subtle shadow
        self.video_frame = ctk.CTkFrame(
            self,
            fg_color=self.colors['card_bg'],
            corner_radius=12,
            border_width=1,
            border_color=self.colors['border']
        )
        self.video_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Clean header
        header_frame = ctk.CTkFrame(self.video_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 0))
        
        self.video_title = ctk.CTkLabel(
            header_frame,
            text="Live Camera Feed",
            font=ctk.CTkFont(family="SF Pro Display", size=22, weight="bold"),
            text_color=self.colors['text_primary']
        )
        self.video_title.pack(side="left")
        
        # Status indicator
        self.camera_status = ctk.CTkLabel(
            header_frame,
            text="● ACTIVE",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['success']
        )
        self.camera_status.pack(side="right")
        
        # Video display area
        self.video_display = ctk.CTkFrame(
            self.video_frame,
            fg_color="#f1f3f4",
            corner_radius=8,
            height=500
        )
        self.video_display.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Professional video canvas
        self.video_canvas = Canvas(
            self.video_display,
            bg=self.colors['background'],
            highlightthickness=0
        )
        self.video_canvas.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Video label for actual video display
        self.video_label = ctk.CTkLabel(self.video_display, text="")
        self.video_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Detection visualizer
        self.detection_viz = DetectionVisualizer(self.video_canvas)
        
        # Processing indicator
        self.processing_indicator = ProfessionalLoadingIndicator(self.video_display, 40)
        
    def create_analysis_panel(self):
        # Analysis panel
        self.analysis_frame = ctk.CTkFrame(
            self,
            fg_color=self.colors['card_bg'],
            corner_radius=12,
            border_width=1,
            border_color=self.colors['border']
        )
        self.analysis_frame.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
        
        # Header
        header_frame = ctk.CTkFrame(self.analysis_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 0))
        
        self.analysis_title = ctk.CTkLabel(
            header_frame,
            text="Medicine Analysis",
            font=ctk.CTkFont(family="SF Pro Display", size=22, weight="bold"),
            text_color=self.colors['text_primary']
        )
        self.analysis_title.pack(side="left")
        
        # Content container for smooth transitions
        self.content_container = ctk.CTkFrame(
            self.analysis_frame,
            fg_color="transparent"
        )
        self.content_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create panels
        self.create_valid_medicine_panel()
        self.create_invalid_medicine_panel()
        self.create_processing_panel()
        
        # Show initial state
        self.show_waiting_panel()
        
    def create_processing_panel(self):
        """Professional processing state"""
        self.processing_panel = ctk.CTkFrame(
            self.content_container,
            fg_color="transparent"
        )
        
        # Processing indicator
        processing_frame = ctk.CTkFrame(
            self.processing_panel,
            fg_color="#f8f9fa",
            corner_radius=12,
            border_width=1,
            border_color=self.colors['border']
        )
        processing_frame.pack(expand=True, fill="both")
        
        self.processing_main_indicator = ProfessionalLoadingIndicator(processing_frame, 60)
        
        self.processing_text = ctk.CTkLabel(
            processing_frame,
            text="Analyzing Medicine...",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['text_secondary']
        )
        self.processing_text.pack(expand=True)
        
    def create_valid_medicine_panel(self):
        self.valid_panel = ctk.CTkFrame(
            self.content_container,
            fg_color="transparent"
        )
        
        # Status header
        self.status_frame = ctk.CTkFrame(
            self.valid_panel,
            fg_color="#d4edda",
            corner_radius=8,
            border_width=1,
            border_color="#c3e6cb"
        )
        self.status_frame.pack(fill="x", pady=(0, 20))
        
        status_content = ctk.CTkFrame(self.status_frame, fg_color="transparent")
        status_content.pack(padx=20, pady=15)
        
        self.status_icon = ctk.CTkLabel(
            status_content,
            text="✓",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors['success']
        )
        self.status_icon.pack(side="left", padx=(0, 10))
        
        self.status_text = ctk.CTkLabel(
            status_content,
            text="VERIFIED MEDICINE",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['success']
        )
        self.status_text.pack(side="left")
        
        # Scrollable content area
        self.info_container = ctk.CTkScrollableFrame(
            self.valid_panel,
            fg_color="transparent"
        )
        self.info_container.pack(fill="both", expand=True)
        
        # Medicine information fields
        self.medicine_fields = {}
        self.create_info_fields()
        
    def create_info_fields(self):
        """Create professional information fields"""
        fields_data = [
            ("name", "Medicine Name", "No data"),
            ("value", "Database Value", "No data"),
            ("batch", "Batch Number", "No data"),
            ("expiry", "Expiry Date", "No data"),
            ("license", "License", "No data"),
            ("manufacturer", "Manufacturer", "No data"),
            ("alternatives", "Alternatives", "No data"),
            ("ocr_analysis", "OCR Analysis", "No data")
        ]
        
        for field_id, label_text, value_text in fields_data:
            field_frame = ctk.CTkFrame(
                self.info_container,
                fg_color="#ffffff",
                corner_radius=8,
                border_width=1,
                border_color=self.colors['border']
            )
            
            # Label
            label = ctk.CTkLabel(
                field_frame,
                text=label_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.colors['text_secondary'],
                anchor="w"
            )
            label.pack(fill="x", padx=15, pady=(12, 2))
            
            # Value
            value_label = ctk.CTkLabel(
                field_frame,
                text=value_text,
                font=ctk.CTkFont(size=14),
                text_color=self.colors['text_primary'],
                anchor="w",
                wraplength=350
            )
            value_label.pack(fill="x", padx=15, pady=(0, 12))
            
            self.medicine_fields[field_id] = {
                'frame': field_frame,
                'value': value_label,
                'current_text': value_text
            }
            
            field_frame.pack(fill="x", pady=3)
        
    def create_invalid_medicine_panel(self):
        self.invalid_panel = ctk.CTkFrame(
            self.content_container,
            fg_color="transparent"
        )
        
        # Error status
        error_frame = ctk.CTkFrame(
            self.invalid_panel,
            fg_color="#f8d7da",
            corner_radius=8,
            border_width=1,
            border_color="#f5c6cb"
        )
        error_frame.pack(fill="x", pady=(0, 20))
        
        error_content = ctk.CTkFrame(error_frame, fg_color="transparent")
        error_content.pack(padx=20, pady=15)
        
        self.error_icon = ctk.CTkLabel(
            error_content,
            text="⚠",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors['error']
        )
        self.error_icon.pack(side="left", padx=(0, 10))
        
        self.error_text = ctk.CTkLabel(
            error_content,
            text="INVALID MEDICINE DETECTED",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['error']
        )
        self.error_text.pack(side="left")
        
        # OCR data display for invalid medicines
        self.invalid_info_container = ctk.CTkScrollableFrame(
            self.invalid_panel,
            fg_color="transparent"
        )
        self.invalid_info_container.pack(fill="both", expand=True)
        
        # Create OCR fields for invalid medicines
        self.invalid_fields = {}
        ocr_fields_data = [
            ("ocr_name", "Detected Name", "No data"),
            ("ocr_batch", "Batch Number", "No data"),
            ("ocr_expiry", "Expiry Date", "No data"),
            ("ocr_license", "License", "No data"),
            ("ocr_manufacturer", "Manufacturer", "No data"),
            ("db_lookup", "Database Lookup", "No data")
        ]
        
        for field_id, label_text, value_text in ocr_fields_data:
            field_frame = ctk.CTkFrame(
                self.invalid_info_container,
                fg_color="#ffffff",
                corner_radius=8,
                border_width=1,
                border_color=self.colors['border']
            )
            
            # Label
            label = ctk.CTkLabel(
                field_frame,
                text=label_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.colors['text_secondary'],
                anchor="w"
            )
            label.pack(fill="x", padx=15, pady=(12, 2))
            
            # Value
            value_label = ctk.CTkLabel(
                field_frame,
                text=value_text,
                font=ctk.CTkFont(size=14),
                text_color=self.colors['text_primary'],
                anchor="w",
                wraplength=350
            )
            value_label.pack(fill="x", padx=15, pady=(0, 12))
            
            self.invalid_fields[field_id] = {
                'frame': field_frame,
                'value': value_label,
                'current_text': value_text
            }
            
            field_frame.pack(fill="x", pady=3)
        
    def create_status_bar(self):
        # Professional status bar
        self.status_bar = ctk.CTkFrame(
            self,
            fg_color=self.colors['card_bg'],
            corner_radius=8,
            height=50,
            border_width=1,
            border_color=self.colors['border']
        )
        self.status_bar.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")
        self.status_bar.grid_propagate(False)
        
        # Status content
        status_content = ctk.CTkFrame(self.status_bar, fg_color="transparent")
        status_content.pack(fill="both", expand=True, padx=20, pady=12)
        
        # System status
        self.system_status = ctk.CTkLabel(
            status_content,
            text="● System Online",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['success']
        )
        self.system_status.pack(side="left")
        
        # Processing status
        self.processing_status = ctk.CTkLabel(
            status_content,
            text="Waiting for input...",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary']
        )
        self.processing_status.pack(side="left", padx=(30, 0))
        
        # Reset button
        self.reset_button = ctk.CTkButton(
            status_content,
            text="RESET",
            width=100,
            height=28,
            fg_color=self.colors['error'],
            hover_color="#c82333",
            corner_radius=6,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.reset_analysis
        )
        self.reset_button.pack(side="right")
        
    def show_waiting_panel(self):
        """Show waiting state"""
        self.hide_all_panels()
        # Create a simple waiting message
        waiting_frame = ctk.CTkFrame(
            self.content_container,
            fg_color="#f8f9fa",
            corner_radius=12,
            border_width=1,
            border_color=self.colors['border']
        )
        waiting_frame.pack(expand=True, fill="both")
        
        waiting_text = ctk.CTkLabel(
            waiting_frame,
            text="Waiting for input...",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['text_secondary']
        )
        waiting_text.pack(expand=True)
        
    def show_processing_panel(self):
        """Show processing panel with professional transition"""
        self.hide_all_panels()
        self.processing_panel.pack(fill="both", expand=True)
        self.processing_main_indicator.start()
        
    def show_valid_panel(self):
        """Show valid medicine panel with slide-in animations"""
        self.hide_all_panels()
        self.valid_panel.pack(fill="both", expand=True)
        
        # Animate fields sliding in sequentially
        for i, (field_id, field_data) in enumerate(self.medicine_fields.items()):
            delay = i * 50  # Stagger the animations
            self.after(delay, lambda f=field_data['frame']: self.animate_field_slide_in(f))
        
    def show_invalid_panel(self):
        """Show invalid medicine panel"""
        self.hide_all_panels()
        self.invalid_panel.pack(fill="both", expand=True)
        
        # Animate fields for invalid panel too
        for i, (field_id, field_data) in enumerate(self.invalid_fields.items()):
            delay = i * 50  # Stagger the animations
            self.after(delay, lambda f=field_data['frame']: self.animate_field_slide_in(f))
        
    def hide_all_panels(self):
        """Hide all content panels"""
        self.processing_main_indicator.stop()
        for child in self.content_container.winfo_children():
            child.pack_forget()
    
    def animate_field_slide_in(self, field_frame):
        """Animate individual field sliding in"""
        # Store original position
        field_frame.pack_forget()
        
        # Create temporary frame for animation
        temp_frame = ctk.CTkFrame(
            field_frame.master,
            fg_color="transparent",
            height=field_frame.winfo_reqheight()
        )
        temp_frame.pack(fill="x", pady=3)
        
        # Animate slide in
        def slide_step(offset=300):
            if offset > 0:
                # Move field frame
                field_frame.place(in_=temp_frame, x=-offset, y=0, relwidth=1)
                temp_frame.after(16, lambda: slide_step(offset - 15))
            else:
                # Animation complete - restore normal packing
                field_frame.place_forget()
                temp_frame.destroy()
                field_frame.pack(fill="x", pady=3)
        
        slide_step()
    
    def update_medicine_field(self, field_id, new_value):
        """Update a medicine field with animation"""
        if field_id in self.medicine_fields:
            field_data = self.medicine_fields[field_id]
            if field_data['current_text'] != new_value:
                # Flash animation for value change
                FieldAnimator.value_change_flash(field_data['frame'], new_value)
                field_data['value'].configure(text=new_value)
                field_data['current_text'] = new_value
                
    def update_invalid_field(self, field_id, new_value):
        """Update an invalid medicine field with animation"""
        if field_id in self.invalid_fields:
            field_data = self.invalid_fields[field_id]
            if field_data['current_text'] != new_value:
                # Flash animation for value change
                FieldAnimator.value_change_flash(field_data['frame'], new_value)
                field_data['value'].configure(text=new_value)
                field_data['current_text'] = new_value
    
    def update_video(self):
        """Update video display"""
        frame, *_ = self.reader.read_frame()
        if frame is not None:
            # Store current frame for capture
            self.current_frame = frame.copy()
            
            # Display frame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img.resize((640, 480)))
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        
        self.after(30, self.update_video)
    
    def setup_serial(self):
        """Setup serial connection"""
        self.serial_port = "/dev/ttyUSB0"  # change to "COM5" if on Windows
        self.baudrate = 115200
        try:
            self.ser = serial.Serial(self.serial_port, self.baudrate, timeout=1)
            self.running = True
            threading.Thread(target=self.read_serial, daemon=True).start()
            self.log_serial("Serial connection established")
        except Exception as e:
            print(f"Serial connection error: {e}")
            self.ser = None
            self.running = False
            self.log_serial(f"Serial connection failed: {e}")
    
    def read_serial(self):
        """Read serial data in separate thread"""
        while self.running and self.ser:
            if self.ser.in_waiting > 0:
                try:
                    data = self.ser.readline().decode().strip()
                    if data:
                        self.log_serial(f"Received: {data}")
                        if data == '1' and not self.processing:
                            # Start analysis
                            self.start_analysis()
                        elif data == '0':
                            # Reset analysis
                            self.reset_analysis()
                except Exception as e:
                    print(f"Serial read error: {e}")
                    self.log_serial(f"Serial read error: {e}")
    
    def start_analysis(self):
        """Start the medicine analysis process"""
        if self.processing:
            return
        
        self.processing = True
        self.detection_in_progress = True
        self.log_serial("Starting analysis...")
        
        # Show processing state
        self.show_processing_panel()
        self.detection_viz.start_detection()
        
        # Update status
        self.processing_status.configure(text="Analyzing Medicine...")
        
        # Start analysis in separate thread
        threading.Thread(target=self.analysis_thread, daemon=True).start()
    
    def analysis_thread(self):
        """Main analysis thread"""
        try:
            # Step 1: Capture image
            self.update_status("Capturing image...")
            if hasattr(self, 'current_frame'):
                self.captured_frame = self.current_frame.copy()
            else:
                self.update_status("Error: No frame available")
                self.processing = False
                self.detection_in_progress = False
                return
            
            # Step 2: UCO Detection
            self.update_status("Detecting medicine with YOLO...")
            time.sleep(1)  # Sleep for 1 second as requested
            
            uco_result = self.detect_medicine()
            is_valid_medicine = uco_result is not None
            
            # Step 3: OCR Analysis (now done before database lookup)
            self.update_status("Performing OCR analysis...")
            ocr_result = self.perform_ocr()
            
            # Step 4: Database lookup (method depends on YOLO result)
            self.update_status("Fetching medicine data from database...")
            if is_valid_medicine:
                # Valid detection - use YOLO value for database lookup
                db_result = self.fetch_medicine_data_by_value(uco_result)
            else:
                # Invalid detection - use OCR name for database lookup
                medicine_name = getattr(ocr_result, 'name', None) if ocr_result else None
                if medicine_name:
                    db_result = self.fetch_medicine_data_by_name(medicine_name)
                else:
                    db_result = None
                    self.log_serial("No medicine name found in OCR for database lookup")
            
            # Stop visual indicators
            self.detection_viz.stop_detection()
            
            # Update UI with results
            self.display_results(db_result, ocr_result, is_valid_medicine)
            
            self.update_status("Analysis complete. Waiting for next input...")
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            self.log_serial(f"Analysis error: {str(e)}")
            self.detection_viz.stop_detection()
        finally:
            self.processing = False
            self.detection_in_progress = False
    
    def detect_medicine(self):
        """Detect medicine using YOLO with retry logic"""
        for attempt in range(3):
            self.update_status(f"YOLO detection attempt {attempt + 1}/3...")
            
            # Use the YOLO model directly on captured frame
            results = self.reader.model.predict(self.captured_frame, conf=self.reader.conf, verbose=False)
            
            detections = []
            for box in results[0].boxes:
                cls_id = int(box.cls[0])
                cls_name = self.reader.model.names[cls_id]
                conf = float(box.conf[0])
                detections.append({"class": cls_name, "confidence": conf})
            
            if detections:
                top_detection = max(detections, key=lambda x: x["confidence"])
                self.log_serial(f"Detection: {top_detection['class']} ({top_detection['confidence']:.2f})")
                
                # Use the UCO reader's mapping logic
                class_name = top_detection['class']
                numeric_id = self.reader.class_to_id.get(class_name)
                
                if numeric_id and numeric_id in self.reader.marker_mapping:
                    uco_value = self.reader.marker_mapping[numeric_id]
                    self.log_serial(f"Mapped to UCO value: {uco_value}")
                    return int(uco_value)  # Convert to int for database lookup
                else:
                    self.log_serial(f"No mapping found for class: {class_name}")
            else:
                self.log_serial(f"No detections in attempt {attempt + 1}")
            
            time.sleep(0.5)  # Wait before retry
        
        self.log_serial("All detection attempts failed")
        return None
    
    def fetch_medicine_data_by_value(self, value):
        """Fetch medicine data from database by value"""
        try:
            document = get_document_by_value(value)
            if document:
                self.log_serial(f"Database lookup by value successful: {document.get('name', 'N/A')}")
            else:
                self.log_serial(f"No document found for value: {value}")
            return document
        except Exception as e:
            self.log_serial(f"Database error (by value): {str(e)}")
            return None
    
    def fetch_medicine_data_by_name(self, name):
        """Fetch medicine data from database by name"""
        try:
            document = get_document_by_name(name)
            if document:
                self.log_serial(f"Database lookup by name successful: {document.get('name', 'N/A')}")
            else:
                self.log_serial(f"No document found for name: {name}")
            return document
        except Exception as e:
            self.log_serial(f"Database error (by name): {str(e)}")
            return None
    
    def perform_ocr(self):
        """Perform OCR on captured frame"""
        try:
            # Save frame to temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            cv2.imwrite(temp_file.name, self.captured_frame)
            
            # Perform OCR
            ocr_data = get_medicine_data(temp_file.name)
            
            # Clean up temporary file
            os.unlink(temp_file.name)
            
            return ocr_data
        except Exception as e:
            self.log_serial(f"OCR error: {str(e)}")
            return None
    
    def display_results(self, db_result, ocr_result, is_valid_medicine):
        """Display all results in UI with modern animations"""
        if is_valid_medicine:
            # Show valid medicine panel
            self.show_valid_panel()
            self.processing_status.configure(text="Medicine Verified Successfully")
            
            # Update medicine fields
            if db_result:
                self.update_medicine_field("name", db_result.get('name', 'N/A'))
                self.update_medicine_field("value", str(db_result.get('value', 'N/A')))
                
                # Format alternatives nicely
                alternatives = db_result.get('alternatives', {})
                if alternatives:
                    alt_text = "\n".join([f"{key}: {value}" for key, value in alternatives.items()])
                    self.update_medicine_field("alternatives", alt_text)
                else:
                    self.update_medicine_field("alternatives", "No alternatives available")
            else:
                self.update_medicine_field("name", "Database lookup failed")
                self.update_medicine_field("value", "N/A")
                self.update_medicine_field("alternatives", "N/A")
            
            # Update OCR fields
            if ocr_result:
                self.update_medicine_field("batch", getattr(ocr_result, 'Batch_number', 'N/A'))
                self.update_medicine_field("expiry", getattr(ocr_result, 'expiry', 'N/A'))
                self.update_medicine_field("license", getattr(ocr_result, 'LIC', 'N/A'))
                self.update_medicine_field("manufacturer", getattr(ocr_result, 'Manufacturer', 'N/A'))
                
                # Format OCR analysis
                ocr_text = f"Name: {getattr(ocr_result, 'name', 'N/A')}\n"
                ocr_text += f"Batch: {getattr(ocr_result, 'Batch_number', 'N/A')}\n"
                ocr_text += f"Expiry: {getattr(ocr_result, 'expiry', 'N/A')}\n"
                ocr_text += f"License: {getattr(ocr_result, 'LIC', 'N/A')}\n"
                ocr_text += f"Manufacturer: {getattr(ocr_result, 'Manufacturer', 'N/A')}"
                self.update_medicine_field("ocr_analysis", ocr_text)
            else:
                self.update_medicine_field("batch", "OCR failed")
                self.update_medicine_field("expiry", "OCR failed")
                self.update_medicine_field("license", "OCR failed")
                self.update_medicine_field("manufacturer", "OCR failed")
                self.update_medicine_field("ocr_analysis", "OCR analysis failed")
                
        else:
            # Show invalid medicine panel
            self.show_invalid_panel()
            self.processing_status.configure(text="Invalid Medicine Detected")
            
            # Update OCR fields for invalid medicine
            if ocr_result:
                self.update_invalid_field("ocr_name", getattr(ocr_result, 'name', 'N/A'))
                self.update_invalid_field("ocr_batch", getattr(ocr_result, 'Batch_number', 'N/A'))
                self.update_invalid_field("ocr_expiry", getattr(ocr_result, 'expiry', 'N/A'))
                self.update_invalid_field("ocr_license", getattr(ocr_result, 'LIC', 'N/A'))
                self.update_invalid_field("ocr_manufacturer", getattr(ocr_result, 'Manufacturer', 'N/A'))
            else:
                self.update_invalid_field("ocr_name", "OCR failed")
                self.update_invalid_field("ocr_batch", "OCR failed")
                self.update_invalid_field("ocr_expiry", "OCR failed")
                self.update_invalid_field("ocr_license", "OCR failed")
                self.update_invalid_field("ocr_manufacturer", "OCR failed")
            
            # Update database lookup result
            if db_result:
                lookup_text = f"Found: {db_result.get('name', 'N/A')}"
                self.update_invalid_field("db_lookup", lookup_text)
            else:
                self.update_invalid_field("db_lookup", "No matching medicine found in database")
    
    def update_status(self, message):
        """Update status label and processing text"""
        self.processing_status.configure(text=message)
        if hasattr(self, 'processing_text'):
            self.processing_text.configure(text=message)
        self.log_serial(f"Status: {message}")
    
    def log_serial(self, message):
        """Add message to console log (since we don't have a serial log textbox in new UI)"""
        print(f"[{time.strftime('%H:%M:%S')}] {message}")
    
    def reset_analysis(self):
        """Reset all analysis data and UI"""
        self.processing = False
        self.detection_in_progress = False
        self.current_step = ""
        self.captured_frame = None
        
        # Stop any ongoing animations
        self.detection_viz.stop_detection()
        
        # Reset UI elements
        self.update_status("Reset complete. Waiting for input...")
        
        # Show waiting state
        self.show_waiting_panel()
        
        # Reset field values
        for field_id, field_data in self.medicine_fields.items():
            field_data['value'].configure(text="No data")
            field_data['current_text'] = "No data"
            
        for field_id, field_data in self.invalid_fields.items():
            field_data['value'].configure(text="No data")
            field_data['current_text'] = "No data"
        
        self.log_serial("System reset")
    
    def on_closing(self):
        """Clean up on closing"""
        self.running = False
        if hasattr(self, 'ser') and self.ser:
            self.ser.close()
        self.reader.release()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()