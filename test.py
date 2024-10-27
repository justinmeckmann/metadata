import os
import piexif

from PIL import Image, ExifTags
from transformers import CLIPProcessor, CLIPModel
import torch


img_filepath = r"/Users/justinmeckmann/Library/CloudStorage/Dropbox/03_Fotos/01_Export/04_Stockphotos/2024/"


# def extract_image_metadata(image_path):
#     image = Image.open(image_path)
#     exif_data = piexif.load(image.info['exif'])

#     # Access specific metadata fields if they exist
#     title = exif_data.get('0th', {}).get(piexif.ImageIFD.ImageDescription, "No title")
#     keywords = exif_data.get('0th', {}).get(piexif.ImageIFD.XPKeywords, "No keywords")
    
#     # Decode keywords if they are stored as bytes
#     if isinstance(keywords, bytes):
#         keywords = keywords.decode('utf-16')  # Adjust encoding if needed
    
#     return title, keywords


# for filename in os.listdir(path=img_filepath):
#     title, keywords = extract_image_metadata(img_filepath + filename)
#     print(title, keywords)

# Load the CLIP model
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")


def generate_keywords(image_path):
    image = Image.open(image_path)
    inputs = clip_processor(images=image, return_tensors="pt")
    outputs = clip_model.get_image_features(**inputs)
    keywords = outputs.topk(5).indices  # Get the top 5 predicted keywords (as indices)

    # Convert indices to words (requires further processing based on your application)
    # Here you'd map indices to words if you have a vocabulary or use pre-defined classes
    return keywords

for filename in os.listdir(path=img_filepath):
    title, keywords = generate_keywords(img_filepath + filename)
    print("Generated Keywords:", keywords)



