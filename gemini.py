import cv2
import base64
import google.generativeai as genai
from dotenv import load_dotenv
import os
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# API config
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(model_name="gemini-2.5-flash")

prompt = """
    Analyze the provided image and extract the following details.
    Return the output as a clean JSON object only, without any markdown formatting or any other text.
    The required JSON schema is:
    {
        "name": "string",
        "Batch number": "string",
        "expiry": "YYYY-MM-DD" or "YYYY-MM",
        "LIC": "string or number",
        "Manufacturer": "string"
    }
    If a value is not found, please set it to null.
    The LIC here refers to the License number of the medicine (FSSAI number is one of them).
    """

def encode_cv2_image(image):
    _, buffer = cv2.imencode('.png', image)
    return base64.b64encode(buffer).decode('utf-8')

def extract_medicine_info(frame):
    """
    Analyzes an image using the Gemini API to extract structured data.

    This function takes the path to an image file, sends it to the
    Gemini Pro Vision model, and asks it to extract specific details based
    on a predefined schema.

    Args:
        image_path (str): The file path to the input image.

    Returns:
        dict: A dictionary containing the extracted information.
              The schema is {
                  "name": str,
                  "Batch number": str,
                  "expiry": str (in "YYYY-MM-DD" format or "YYYY-MM" format),
                  "LIC": str or int,
                  "Manufacturer": str
              }.
              Returns an error dictionary if the API call fails or the
              response cannot be parsed.
    """
    encoded = encode_cv2_image(frame)
    response = model.generate_content([
        {
            "mime_type": "image/png",
            "data": encoded,
        },
        prompt,
    ])
    return response.text
