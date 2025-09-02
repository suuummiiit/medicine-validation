import cv2
import os
import tkinter as tk
from PIL import Image, ImageTk

# Make sure images directory exists
os.makedirs("images", exist_ok=True)

cap = cv2.VideoCapture(2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)   # 2K width
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1440)  # 2K height

root = tk.Tk()
root.title("Camera App")

# Label to show video
video_label = tk.Label(root)
video_label.pack()

flash_overlay = tk.Label(root, bg="white")
flash_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
flash_overlay.lower()  # hide under video

def update_frame():
    ret, frame = cap.read()
    if ret:
        # Convert BGR to RGB
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)
    video_label.after(10, update_frame)

def capture_image(event=None):
    ret, frame = cap.read()
    if ret:
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        count = len(os.listdir("images")) + 1
        filename = f"images/image_{count}.png"
        cv2.imwrite(filename, frame)
        print(f"Saved {filename}")
        show_flash()

def show_flash():
    flash_overlay.lift()   # bring flash to front
    root.after(100, lambda: flash_overlay.lower())  # hide after 100ms

def on_close():
    cap.release()
    root.destroy()

root.bind("<space>", capture_image)
root.protocol("WM_DELETE_WINDOW", on_close)

update_frame()
root.mainloop()
