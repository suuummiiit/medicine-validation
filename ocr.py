import base64
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional

# Load API key
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

Model = "gpt-4o-mini"

# System message
system_message = """
You are an expert at structured data extraction.
You will be given an image of a medicine package.
You must extract the details and return them in the given structure.
If any value is missing, set it to null.
"""

# Pydantic schema
class MedicineInfo(BaseModel):
    name: Optional[str]
    Batch_number: Optional[str]
    expiry: Optional[str]   # YYYY-MM
    LIC: Optional[str]      # License / FSSAI number
    Manufacturer: Optional[str] # Manufacturer name only


# Function to encode local image to base64
def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Main function
def get_medicine_data(image_path: str) -> MedicineInfo:
    base64_image = encode_image(image_path)

    completion = client.beta.chat.completions.parse(
        model=Model,
        messages=[
            {"role": "system", "content": system_message},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                ],
            },
        ],
        response_format=MedicineInfo,
    )

    return completion.choices[0].message.parsed


# Example usage
if __name__ == "__main__":
    image_path = "test/test.jpg"  # Change this to your local image path
    data = get_medicine_data(image_path)
    print("OCR OUTPUT")
    print(data)
    print(type(data))

    # print("Pydantic object:", data)
    # print("As dict:", data.model_dump())
