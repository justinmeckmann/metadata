import os
import pyexiv2
import re
import contextlib
import io
import sys

img_filepath = r"C:/Users/justi/Dropbox/03_Fotos/01_Export/04_Stockphotos/2024/"

@contextlib.contextmanager
def suppress_stdout_stderr():
    new_stdout, new_stderr = io.StringIO(), io.StringIO()
    old_stdout, old_stderr = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_stdout, new_stderr
        yield
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr

def clean_text(text):
    if text is None:
        return None
    if isinstance(text, dict):
        text = next(iter(text.values()), '')
    text = str(text)
    text = text.replace('(', '-')
    text = re.sub(r'[/),]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_and_clean_metadata(image_path):
    try:
        with suppress_stdout_stderr(), pyexiv2.Image(image_path) as img:
            xmp = img.read_xmp()
            iptc = img.read_iptc()
            exif = img.read_exif()

            title = clean_text(xmp.get('Xmp.dc.title') or 
                               iptc.get('Iptc.Application2.ObjectName') or 
                               exif.get('Exif.Image.ImageDescription'))
            
            keywords = xmp.get('Xmp.dc.subject') or iptc.get('Iptc.Application2.Keywords') or exif.get('Exif.Image.XPKeywords')
            if isinstance(keywords, str):
                keywords = [clean_text(k.strip()) for k in keywords.split(',')]
            elif isinstance(keywords, (list, tuple)):
                keywords = [clean_text(k) for k in keywords]
            else:
                keywords = []

            description = clean_text(xmp.get('Xmp.dc.description') or
                                     iptc.get('Iptc.Application2.Caption') or
                                     exif.get('Exif.Image.ImageDescription') or
                                     xmp.get('Xmp.exif.UserComment'))

            return title, keywords, description

    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")
        return None, None, None

def write_metadata(image_path, title, keywords, description):
    try:
        with suppress_stdout_stderr(), pyexiv2.Image(image_path) as img:
            # Update XMP metadata
            xmp = img.read_xmp()
            if title:
                xmp['Xmp.dc.title'] = title  # Changed this line
            if keywords:
                xmp['Xmp.dc.subject'] = keywords
            if description:
                xmp['Xmp.dc.description'] = description  # Changed this line too
            img.modify_xmp(xmp)

            # Update IPTC metadata
            iptc = img.read_iptc()
            if title:
                iptc['Iptc.Application2.ObjectName'] = title
            if keywords:
                iptc['Iptc.Application2.Keywords'] = keywords
            if description:
                iptc['Iptc.Application2.Caption'] = description
            img.modify_iptc(iptc)

            # Update EXIF metadata
            exif = img.read_exif()
            if title:
                exif['Exif.Image.XPTitle'] = title.encode('utf-16le')
            if description:
                exif['Exif.Image.ImageDescription'] = description
            
            # Remove problematic thumbnail data
            exif.pop('Exif.Thumbnail.JPEGInterchangeFormat', None)
            exif.pop('Exif.Thumbnail.JPEGInterchangeFormatLength', None)
            
            img.modify_exif(exif)

        print(f"Metadata updated for {image_path}")
    except Exception as e:
        print(f"Error updating metadata for {image_path}: {str(e)}")

for filename in os.listdir(path=img_filepath):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        img_path = os.path.join(img_filepath, filename)
        title, keywords, description = extract_and_clean_metadata(img_path)
        
        print(f"\nFile: {filename}")
        print(f"Title: {title}")
        print(f"Keywords: {keywords}")
        print(f"Description: {description}")
        
        # Write the cleaned metadata back to the file
        write_metadata(img_path, title, keywords, description)
        
        print("-" * 30)
