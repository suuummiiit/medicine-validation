import cv2
import tkinter as tk
from PIL import Image, ImageTk
from ultralytics import YOLO

# Load YOLO model
model = YOLO("best.pt")

cap = cv2.VideoCapture(2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)   # optional, adjust if needed
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

root = tk.Tk()
root.title("YOLO Live Camera")

video_label = tk.Label(root)
video_label.pack()


def update_frame():
    ret, frame = cap.read()
    if ret:
        # Rotate 180 degrees
        frame = cv2.rotate(frame, cv2.ROTATE_180)

        # Run YOLO inference
        results = model(frame)[0]

        # Filter only the detection with highest confidence
        if len(results.boxes) > 0:
            # Find index of box with max confidence
            max_conf_idx = results.boxes.conf.argmax()
            results.boxes = results.boxes[max_conf_idx:max_conf_idx+1]

        # Annotate frame
        annotated_frame = results.plot()

        # Convert BGR->RGB for Tkinter
        cv2image = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)

    video_label.after(10, update_frame)


def on_close():
    cap.release()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
update_frame()
root.mainloop()
