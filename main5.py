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
    def value_change_flash(widget, new_text, color="#e8f8e8"):
        """Subtle flash animation when values change"""
        original_color = widget.cget("fg_color")
        
        # Flash effect with medical green tint
        widget.configure(fg_color=color)
        
        def restore_color():
            widget.configure(fg_color=original_color)
        
        widget.after(200, restore_color)

class ProfessionalLoadingIndicator:
    """Elegant loading indicator for processing states with medical theme"""
    
    def __init__(self, parent, size=30):
        self.parent = parent
        self.size = size
        self.angle = 0
        self.is_active = False
        
        self.canvas = Canvas(
            parent,
            width=size,
            height=size,
            bg='#f0f8f0',  # Light medical green background
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
            
            # Medical-themed circular indicator with green tones
            for i in range(12):
                angle = self.angle + i * 30
                x1 = center + radius * 0.8 * math.cos(math.radians(angle))
                y1 = center + radius * 0.8 * math.sin(math.radians(angle))
                x2 = center + radius * math.cos(math.radians(angle))
                y2 = center + radius * math.sin(math.radians(angle))
                
                alpha = max(0.15, 1.0 - i * 0.08)
                # Medical green color progression
                green_val = int(120 + alpha * 100)
                red_val = int(40 + alpha * 60)
                blue_val = int(40 + alpha * 60)
                
                self.canvas.create_line(
                    x1, y1, x2, y2,
                    fill=f"#{red_val:02x}{green_val:02x}{blue_val:02x}",
                    width=2, capstyle="round", tags="indicator"
                )
            
            self.angle += 10
            self.parent.after(50, self.animate)

class DetectionVisualizer:
    """Professional detection visualization with medical theme"""
    
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
            # Enhanced scanning beam with faster movement and medical green colors
            beam_height = 4
            self.scan_y += self.scan_direction * 4  # Increased speed from 2 to 4
            
            if self.scan_y >= height - beam_height:
                self.scan_direction = -1
            elif self.scan_y <= 0:
                self.scan_direction = 1
            
            # Create gradient scanning beam with medical green theme
            for i in range(beam_height):
                y = self.scan_y + i
                if 0 <= y < height:
                    alpha = 1.0 - (i / beam_height)
                    # Medical green scanning beam
                    red_val = int(40 + alpha * 60)
                    green_val = int(180 + alpha * 75)
                    blue_val = int(80 + alpha * 60)
                    self.canvas.create_line(
                        0, y, width, y,
                        fill=f"#{red_val:02x}{green_val:02x}{blue_val:02x}",
                        width=2, tags="detection"
                    )
            
            # Medical-themed detection grid overlay
            grid_spacing = 60
            for x in range(0, width, grid_spacing):
                alpha = 0.2
                # Light medical green grid lines
                self.canvas.create_line(
                    x, 0, x, height,
                    fill="#c8e6c8",
                    width=1, tags="detection"
                )
            
            for y in range(0, height, grid_spacing):
                alpha = 0.2
                # Light medical green grid lines
                self.canvas.create_line(
                    0, y, width, y,
                    fill="#c8e6c8",
                    width=1, tags="detection"
                )
        
        self.canvas.after(25, self.animate_detection)  # Reduced from 40 to 25 for faster animation

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window setup with medical theme
        self.title("MedGuard - Medical Scanner System")
        self.geometry("1400x900")
        self.configure(fg_color="#f0f8f5")  # Light medical green background
        
        # Enhanced medical color scheme
        self.colors = {
            'background': '#f0f8f5',  # Light medical green
            'card_bg': '#ffffff',
            'text_primary': '#1a1a1a',
            'text_secondary': '#5a6c5a',  # Subtle green tint
            'success': '#22c55e',  # Medical green
            'error': '#ef4444',
            'warning': '#f59e0b',
            'info': '#3b82f6',
            'border': '#d1e7dd',  # Light medical green border
            'shadow': '#00000010',
            'accent': '#16a085',  # Medical teal
            'medical_primary': '#22c55e',  # Primary medical green
            'medical_secondary': '#86efac',  # Light medical green
            'medical_tertiary': '#dcfce7'  # Very light medical green
        }
        
        # State variables
        self.processing = False
        self.should_stop_processing = False  # Flag to stop processing
        self.current_step = ""
        self.captured_frame = None
        self.current_frame = None
        self.detection_in_progress = False
        
        # YOLO reader - change cam_index to your camera device ID
        self.camera_index = 0  # Change this value to your camera device ID
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
        # Video panel with medical theme and subtle medical green accent
        self.video_frame = ctk.CTkFrame(
            self,
            fg_color=self.colors['card_bg'],
            corner_radius=12,
            border_width=2,
            border_color=self.colors['medical_secondary']
        )
        self.video_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Clean header with medical accent
        header_frame = ctk.CTkFrame(
            self.video_frame, 
            fg_color=self.colors['medical_tertiary'],
            corner_radius=8
        )
        header_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        self.video_title = ctk.CTkLabel(
            header_frame,
            text="🏥 Live Camera Feed",
            font=ctk.CTkFont(family="SF Pro Display", size=22, weight="bold"),
            text_color=self.colors['text_primary']
        )
        self.video_title.pack(side="left", padx=15, pady=10)
        
        # Status indicator with medical styling
        self.camera_status = ctk.CTkLabel(
            header_frame,
            text="● ACTIVE",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['medical_primary']
        )
        self.camera_status.pack(side="right", padx=15, pady=10)
        
        # Video display area with medical border
        self.video_display = ctk.CTkFrame(
            self.video_frame,
            fg_color="#f8fdf8",  # Very light medical green
            corner_radius=8,
            height=500,
            border_width=1,
            border_color=self.colors['medical_secondary']
        )
        self.video_display.pack(padx=20, pady=(0, 20), fill="both", expand=True)
        
        # Medical-themed video canvas with higher z-order for scanning line
        self.video_canvas = Canvas(
            self.video_display,
            bg=self.colors['background'],
            highlightthickness=0
        )
        self.video_canvas.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Video label for actual video display (lower z-order)
        self.video_label = ctk.CTkLabel(self.video_display, text="")
        self.video_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Make sure canvas is above the video label
        self.video_canvas.lift()
        
        # Detection visualizer
        self.detection_viz = DetectionVisualizer(self.video_canvas)
        
        # Processing indicator with medical theme
        self.processing_indicator = ProfessionalLoadingIndicator(self.video_display, 40)
        
    def create_analysis_panel(self):
        # Analysis panel with medical theming
        self.analysis_frame = ctk.CTkFrame(
            self,
            fg_color=self.colors['card_bg'],
            corner_radius=12,
            border_width=2,
            border_color=self.colors['medical_secondary']
        )
        self.analysis_frame.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
        
        # Header with medical accent
        header_frame = ctk.CTkFrame(
            self.analysis_frame, 
            fg_color=self.colors['medical_tertiary'],
            corner_radius=8
        )
        header_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        self.analysis_title = ctk.CTkLabel(
            header_frame,
            text="🔬 Medicine Analysis",
            font=ctk.CTkFont(family="SF Pro Display", size=22, weight="bold"),
            text_color=self.colors['text_primary']
        )
        self.analysis_title.pack(side="left", padx=15, pady=10)
        
        # Content container for smooth transitions
        self.content_container = ctk.CTkFrame(
            self.analysis_frame,
            fg_color="transparent"
        )
        self.content_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create panels
        self.create_result_panel()
        self.create_processing_panel()
        
        # Show initial state
        self.show_waiting_panel()
        
    def create_processing_panel(self):
        """Professional processing state with medical theme"""
        self.processing_panel = ctk.CTkFrame(
            self.content_container,
            fg_color="transparent"
        )
        
        # Processing indicator with medical styling
        processing_frame = ctk.CTkFrame(
            self.processing_panel,
            fg_color=self.colors['medical_tertiary'],
            corner_radius=12,
            border_width=2,
            border_color=self.colors['medical_secondary']
        )
        processing_frame.pack(expand=True, fill="both")
        
        self.processing_main_indicator = ProfessionalLoadingIndicator(processing_frame, 60)
        
        self.processing_text = ctk.CTkLabel(
            processing_frame,
            text="🔍 Starting Analysis...",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['text_secondary']
        )
        self.processing_text.pack(expand=True)
        
    def create_result_panel(self):
        """Create unified result panel for both valid and invalid medicines with medical theme"""
        self.result_panel = ctk.CTkFrame(
            self.content_container,
            fg_color="transparent"
        )
        
        # Status header (will be updated based on validity) - enhanced medical styling
        self.status_frame = ctk.CTkFrame(
            self.result_panel,
            fg_color="#d1f2eb",  # Light medical green
            corner_radius=8,
            border_width=2,
            border_color=self.colors['medical_secondary']
        )
        self.status_frame.pack(fill="x", pady=(0, 20))
        
        status_content = ctk.CTkFrame(self.status_frame, fg_color="transparent")
        status_content.pack(padx=20, pady=15)
        
        self.status_icon = ctk.CTkLabel(
            status_content,
            text="✓",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors['medical_primary']
        )
        self.status_icon.pack(side="left", padx=(0, 10))
        
        self.status_text = ctk.CTkLabel(
            status_content,
            text="VERIFIED MEDICINE",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['medical_primary']
        )
        self.status_text.pack(side="left")
        
        # Scrollable content area with medical styling
        self.info_container = ctk.CTkScrollableFrame(
            self.result_panel,
            fg_color="transparent",
            scrollbar_fg_color=self.colors['medical_tertiary'],
            scrollbar_button_color=self.colors['medical_secondary'],
            scrollbar_button_hover_color=self.colors['medical_primary']
        )
        self.info_container.pack(fill="both", expand=True)
        
        # Medicine information fields - will be created dynamically
        self.result_fields = {}
        
    def create_result_field(self, field_id, label_text, value_text, icon="✓", color="#22c55e"):
        """Create a single result field with icon and medical styling"""
        field_frame = ctk.CTkFrame(
            self.info_container,
            fg_color="#ffffff",
            corner_radius=8,
            border_width=1,
            border_color=self.colors['medical_secondary']
        )
        
        # Header with icon and label - enhanced medical styling
        header_frame = ctk.CTkFrame(
            field_frame, 
            fg_color=self.colors['medical_tertiary'],
            corner_radius=6
        )
        header_frame.pack(fill="x", padx=12, pady=(12, 8))
        
        # Icon
        icon_label = ctk.CTkLabel(
            header_frame,
            text=icon,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=color
        )
        icon_label.pack(side="left", padx=(10, 8), pady=8)
        
        # Label
        label = ctk.CTkLabel(
            header_frame,
            text=label_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['text_secondary'],
            anchor="w"
        )
        label.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=8)
        
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
        
        self.result_fields[field_id] = {
            'frame': field_frame,
            'icon': icon_label,
            'label': label,
            'value': value_label,
            'current_text': value_text
        }
        
        # Initially hide the field (will be shown with animation)
        field_frame.pack_forget()
        
        return field_frame
        
    def show_waiting_panel(self):
        """Show waiting state with medical theme"""
        self.hide_all_panels()
        # Create a medical-themed waiting message
        waiting_frame = ctk.CTkFrame(
            self.content_container,
            fg_color=self.colors['medical_tertiary'],
            corner_radius=12,
            border_width=2,
            border_color=self.colors['medical_secondary']
        )
        waiting_frame.pack(expand=True, fill="both")
        
        waiting_text = ctk.CTkLabel(
            waiting_frame,
            text="⚕️ Ready for Medical Scan...",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['text_secondary']
        )
        waiting_text.pack(expand=True)
        
    def show_processing_panel(self):
        """Show processing panel with professional transition"""
        self.hide_all_panels()
        self.processing_panel.pack(fill="both", expand=True)
        self.processing_main_indicator.start()
        
    def show_result_panel(self, is_valid_medicine):
        """Show result panel with appropriate styling and medical theme"""
        self.hide_all_panels()
        
        # Update status frame based on validity with enhanced medical styling
        if is_valid_medicine:
            self.status_frame.configure(fg_color="#d1f2eb", border_color="#a7f3d0")
            self.status_icon.configure(text="✅", text_color=self.colors['medical_primary'])
            self.status_text.configure(text="✅ VERIFIED MEDICINE", text_color=self.colors['medical_primary'])
        else:
            self.status_frame.configure(fg_color="#fde2e7", border_color="#f5c2c7")
            self.status_icon.configure(text="⚠️", text_color=self.colors['error'])
            self.status_text.configure(text="⚠️ UNVERIFIED MEDICINE DETECTED", text_color=self.colors['error'])
        
        self.result_panel.pack(fill="both", expand=True)
        
    def hide_all_panels(self):
        """Hide all content panels"""
        self.processing_main_indicator.stop()
        for child in self.content_container.winfo_children():
            child.pack_forget()
        
        # Clear existing result fields
        for field_id, field_data in self.result_fields.items():
            field_data['frame'].destroy()
        self.result_fields.clear()
    
    def animate_field_display(self, field_frame, delay=0):
        """Animate field display with medical-themed fade effect"""
        def show_field():
            # Show field with medical fade animation
            field_frame.pack(fill="x", pady=3)
            
            # Medical green fade effect
            original_fg = field_frame.cget("fg_color")
            
            def fade_in(alpha=0.1):
                if alpha <= 1.0:
                    # Simulate fade with light medical green
                    field_frame.configure(fg_color="#ffffff")
                    self.after(20, lambda: fade_in(alpha + 0.1))
            
            fade_in()
        
        if delay > 0:
            self.after(int(delay * 1000), show_field)
        else:
            show_field()
    
    def update_video(self):
        """Update video display - ensure canvas stays on top"""
        frame, *_ = self.reader.read_frame()
        if frame is not None:
            # Rotate frame 180 degrees to correct camera orientation
            rotated_frame = cv2.rotate(frame, cv2.ROTATE_180)
            
            # Store rotated frame for capture and analysis
            self.current_frame = rotated_frame.copy()
            
            # Display rotated frame
            frame_rgb = cv2.cvtColor(rotated_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img.resize((640, 480)))
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        
        self.after(30, self.update_video)
    
    def setup_serial(self):
        """Setup serial connection"""
        self.serial_port = "/dev/ttyUSB0"  # change to "COM5" if on Windows
        self.baudrate = 115200
        # self.baudrate = 9600
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
                        if data == '1':
                            if self.processing:
                                # Reset and restart if already processing
                                self.should_stop_processing = True
                                time.sleep(0.1)  # Give time for current process to stop
                            self.start_analysis()
                        elif data == '0':
                            # Stop processing and reset
                            self.should_stop_processing = True
                            self.reset_analysis()
                except Exception as e:
                    print(f"Serial read error: {e}")
                    self.log_serial(f"Serial read error: {e}")
    
    def start_analysis(self):
        """Start the medicine analysis process"""
        self.processing = True
        self.should_stop_processing = False
        self.detection_in_progress = True
        self.log_serial("Starting new analysis...")
        
        # Show processing state
        self.show_processing_panel()
        self.detection_viz.start_detection()
        
        # Update status
        self.processing_status.configure(text="🔍 Starting Analysis...")
        
        # Start analysis in separate thread
        threading.Thread(target=self.analysis_thread, daemon=True).start()
    
    def analysis_thread(self):
        """Main analysis thread with new workflow"""
        try:
            # Step 0: Capture image first
            self.update_status("📸 Capturing image...")
            if hasattr(self, 'current_frame'):
                self.captured_frame = self.current_frame.copy()
            else:
                self.update_status("❌ Error: No frame available")
                self.processing = False
                self.detection_in_progress = False
                return
            
            # Check if we should stop
            if self.should_stop_processing:
                self.log_serial("Process stopped by user")
                return
            
            # Step 1: OCR Analysis First (don't display results yet)
            self.update_status("🔍 Performing OCR analysis...")
            ocr_result = self.perform_ocr()
            
            # Check if we should stop
            if self.should_stop_processing:
                self.log_serial("Process stopped by user")
                return
            
            # Step 2: UCO Detection with retries
            self.update_status("🎯 Detecting medicine with YOLO...")
            uco_result = self.detect_medicine()
            is_valid_medicine = uco_result is not None
            
            # Check if we should stop
            if self.should_stop_processing:
                self.log_serial("Process stopped by user")
                return
            
            # Step 3: Database lookup based on detection result
            self.update_status("💾 Fetching medicine data from database...")
            if is_valid_medicine:
                # Valid detection - use YOLO value for database lookup
                db_result = self.fetch_medicine_data_by_value(uco_result)
                self.log_serial(f"Valid medicine detected with value: {uco_result}")
            else:
                # Invalid detection - use OCR name for database lookup
                medicine_name = getattr(ocr_result, 'name', None) if ocr_result else None
                if medicine_name:
                    db_result = self.fetch_medicine_data_by_name(medicine_name)
                    self.log_serial(f"Invalid medicine - searching database with name: {medicine_name}")
                else:
                    db_result = None
                    self.log_serial("Invalid medicine - no name found for database lookup")
            
            # Check if we should stop before displaying results
            if self.should_stop_processing:
                self.log_serial("Process stopped by user")
                return
            
            # Stop visual indicators
            self.detection_viz.stop_detection()
            
            # Step 4: Display results with animations
            self.display_results_with_animation(db_result, ocr_result, is_valid_medicine)
            
            self.update_status("✅ Analysis complete. Ready for next scan...")
            
        except Exception as e:
            if not self.should_stop_processing:
                self.update_status(f"❌ Error: {str(e)}")
                self.log_serial(f"Analysis error: {str(e)}")
            self.detection_viz.stop_detection()
        finally:
            self.processing = False
            self.detection_in_progress = False
    
    def detect_medicine(self):
        """Detect medicine using YOLO with retry logic"""
        for attempt in range(3):
            # Check if we should stop
            if self.should_stop_processing:
                return None
                
            self.update_status(f"🎯 YOLO detection attempt {attempt + 1}/3...")
            
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
    
    def display_results_with_animation(self, db_result, ocr_result, is_valid_medicine):
        """Display results with sequential fade animations and medical theme"""
        # Show result panel
        self.show_result_panel(is_valid_medicine)
        
        # Prepare field data based on database and OCR results
        field_sequence = []
        delay_counter = 0
        
        # 1. Medicine Name with medical icon
        if db_result and db_result.get('name'):
            name_field = self.create_result_field(
                "name", 
                "💊 Medicine Name", 
                db_result.get('name', 'N/A'),
                "✅",
                self.colors['medical_primary']
            )
            field_sequence.append((name_field, delay_counter))
            delay_counter += 0.5
        
        # 2. License with medical icon
        if db_result and db_result.get('LIC'):
            lic_field = self.create_result_field(
                "license", 
                "🏥 License", 
                db_result.get('LIC', 'N/A'),
                "✅",
                self.colors['medical_primary']
            )
            field_sequence.append((lic_field, delay_counter))
            delay_counter += 0.5
        
        # 3. Expiry Date with calendar icon
        if db_result and db_result.get('expiry_date'):
            expiry_field = self.create_result_field(
                "expiry", 
                "📅 Expiry Date", 
                db_result.get('expiry_date', 'N/A'),
                "✅",
                self.colors['medical_primary']
            )
            field_sequence.append((expiry_field, delay_counter))
            delay_counter += 0.5
        
        # 4. Batch Number Comparison with enhanced medical styling
        db_batch = db_result.get('batch_number', '') if db_result else ''
        ocr_batch = getattr(ocr_result, 'Batch_number', '') if ocr_result else ''
        
        if db_batch and ocr_batch:
            # Compare batch numbers
            batch_matches = db_batch.strip().lower() == ocr_batch.strip().lower()
            if batch_matches:
                batch_field = self.create_result_field(
                    "batch", 
                    "🔢 Batch Number", 
                    f"✅ Matched: {db_batch}",
                    "✅",
                    self.colors['medical_primary']
                )
            else:
                batch_field = self.create_result_field(
                    "batch", 
                    "🔢 Batch Number", 
                    f"❌ Not Matched\nDB: {db_batch}\nOCR: {ocr_batch}",
                    "⚠️",
                    self.colors['error']
                )
            field_sequence.append((batch_field, delay_counter))
            delay_counter += 0.5
        elif db_batch:
            # Only database batch available
            batch_field = self.create_result_field(
                "batch", 
                "🔢 Batch Number", 
                f"DB: {db_batch}\n(OCR not available)",
                "ℹ️",
                self.colors['warning']
            )
            field_sequence.append((batch_field, delay_counter))
            delay_counter += 0.5
        elif ocr_batch:
            # Only OCR batch available
            batch_field = self.create_result_field(
                "batch", 
                "🔢 Batch Number", 
                f"OCR: {ocr_batch}\n(No DB match)",
                "ℹ️",
                self.colors['warning']
            )
            field_sequence.append((batch_field, delay_counter))
            delay_counter += 0.5
        
        # 5. Alternatives with medical icon
        if db_result and db_result.get('alternatives'):
            alternatives = db_result.get('alternatives', {})
            if alternatives and isinstance(alternatives, dict):
                alt_text = "\n".join([f"• {key}: {value}" for key, value in alternatives.items()])
            else:
                alt_text = "No alternatives available"
            
            alt_field = self.create_result_field(
                "alternatives", 
                "💉 Alternative Medicines", 
                alt_text,
                "ℹ️",
                self.colors['info']
            )
            field_sequence.append((alt_field, delay_counter))
            delay_counter += 0.5
        
        # If no database result was found, show what we got from OCR with medical styling
        if not db_result:
            if ocr_result:
                ocr_info = []
                if hasattr(ocr_result, 'name') and ocr_result.name:
                    ocr_info.append(f"💊 Name: {ocr_result.name}")
                if hasattr(ocr_result, 'Batch_number') and ocr_result.Batch_number:
                    ocr_info.append(f"🔢 Batch: {ocr_result.Batch_number}")
                if hasattr(ocr_result, 'expiry') and ocr_result.expiry:
                    ocr_info.append(f"📅 Expiry: {ocr_result.expiry}")
                if hasattr(ocr_result, 'LIC') and ocr_result.LIC:
                    ocr_info.append(f"🏥 License: {ocr_result.LIC}")
                if hasattr(ocr_result, 'Manufacturer') and ocr_result.Manufacturer:
                    ocr_info.append(f"🏭 Manufacturer: {ocr_result.Manufacturer}")
                
                ocr_text = "\n".join(ocr_info) if ocr_info else "❌ No UCO Marker Detected"
            else:
                ocr_text = "❌ OCR analysis failed"
            
            ocr_field = self.create_result_field(
                "ocr_data", 
                "🔍 Detection Status", 
                ocr_text,
                "ℹ️",
                self.colors['info']
            )
            field_sequence.append((ocr_field, delay_counter))
            delay_counter += 0.5
            
            # Show database lookup status with medical styling
            lookup_field = self.create_result_field(
                "db_status", 
                "💾 Database Status", 
                "❌ No matching medicine found in database",
                "⚠️",
                self.colors['error']
            )
            field_sequence.append((lookup_field, delay_counter))
        
        # Animate all fields with delays
        for field_frame, delay in field_sequence:
            if not self.should_stop_processing:
                self.animate_field_display(field_frame, delay)
    
    def update_status(self, message):
        """Update status label and processing text with medical icons"""
        self.processing_status.configure(text=message)
        if hasattr(self, 'processing_text'):
            self.processing_text.configure(text=message)
        self.log_serial(f"Status: {message}")
    
    def log_serial(self, message):
        """Add message to console log"""
        print(f"[{time.strftime('%H:%M:%S')}] {message}")
    
    def reset_analysis(self):
        """Reset all analysis data and UI"""
        self.should_stop_processing = True
        self.processing = False
        self.detection_in_progress = False
        self.current_step = ""
        self.captured_frame = None
        
        # Stop any ongoing animations
        self.detection_viz.stop_detection()
        
        # Reset UI elements
        self.update_status("🔄 Reset complete. Ready for medical scan...")
        
        # Show waiting state
        self.show_waiting_panel()
        
        self.log_serial("System reset")
    
    def on_closing(self):
        """Clean up on closing"""
        self.running = False
        self.should_stop_processing = True
        if hasattr(self, 'ser') and self.ser:
            self.ser.close()
        self.reader.release()
        self.destroy()

    def create_status_bar(self):
        # Enhanced medical-themed status bar
        self.status_bar = ctk.CTkFrame(
            self,
            fg_color=self.colors['card_bg'],
            corner_radius=8,
            height=50,
            border_width=2,
            border_color=self.colors['medical_secondary']
        )
        self.status_bar.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")
        self.status_bar.grid_propagate(False)
        
        # Status content with medical background
        status_content = ctk.CTkFrame(
            self.status_bar, 
            fg_color=self.colors['medical_tertiary'],
            corner_radius=6
        )
        status_content.pack(fill="both", expand=True, padx=8, pady=8)
        
        # System status with medical styling
        self.system_status = ctk.CTkLabel(
            status_content,
            text="🟢 System Online",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['medical_primary']
        )
        self.system_status.pack(side="left", padx=15, pady=5)
        
        # Processing status with medical icons
        self.processing_status = ctk.CTkLabel(
            status_content,
            text="⚕️ Ready for medical scan...",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary']
        )
        self.processing_status.pack(side="left", padx=(30, 0), pady=5)
        
        # Enhanced reset button with medical styling
        self.reset_button = ctk.CTkButton(
            status_content,
            text="🔄 RESET",
            width=120,
            height=32,
            fg_color=self.colors['error'],
            hover_color="#dc2626",
            corner_radius=6,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.reset_analysis,
            border_width=1,
            border_color="#fca5a5"
        )
        self.reset_button.pack(side="right", padx=15, pady=5)

if __name__ == "__main__":
    app = App()
    app.mainloop()