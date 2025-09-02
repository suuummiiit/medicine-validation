# # main.py
# import cv2
# import json
# from gemini import extract_medicine_info   # import your module

# def main():
#     image_path = "test2.jpg"   # change this to your local image
#     frame = cv2.imread(image_path)

#     if frame is None:
#         print(f"❌ Could not load image: {image_path}")
#         return

#     result = extract_medicine_info(frame)

#     try:
#         data = json.loads(result)
#         print(json.dumps(data, indent=4))
#     except Exception:
#         print("⚠️ Raw response from Gemini:")
#         print(result)

# if __name__ == "__main__":
#     main()



import cv2
from ocr import extract_medicine_info

frame = cv2.imread("test.jpg")
info = extract_medicine_info(frame)

print(info)
print(info.model_dump())
