import os
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get variables from environment
base_dir = os.getenv('BASE_DIR')
crop_area_type = tuple(map(int, os.getenv('CROP_AREA_TYPE').split(',')))
crop_area_name = tuple(map(int, os.getenv('CROP_AREA_NAME').split(',')))

# Function to preprocess and extract text from an image
def extract_text(image_path, crop_area=None, save_crop=False, crop_name="", failed_folder=None):
    image = Image.open(image_path)
    if crop_area:
        image = image.crop(crop_area)
        if save_crop:
            # Save the cropped image for debugging purposes
            crop_debug_path = os.path.join(failed_folder, f"crop_debug_{crop_name}.png")
            image.save(crop_debug_path)
            print(f"Saved cropped image for debugging: {crop_debug_path}")
    
    # Preprocess the image
    image = image.convert('L')  # Convert to grayscale
    image = ImageEnhance.Contrast(image).enhance(2)  # Increase contrast
    image = image.filter(ImageFilter.SHARPEN)  # Sharpen the image
    
    # Apply thresholding to convert the image to pure black and white
    threshold = 128
    image = image.point(lambda p: p > threshold and 255)
    
    # Custom OCR configuration to improve text recognition
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789- '

    text = pytesseract.image_to_string(image, config=custom_config)
    return text

# Function to clean and identify the attachment type and name
def identify_attachment(image_path, failed_folder):
    try:
        # Crop area for attachment type (top left corner)
        attachment_type_text = extract_text(image_path, crop_area=crop_area_type, save_crop=True, crop_name="type", failed_folder=failed_folder).strip()
        print(f"Attachment type text: {attachment_type_text}")

        # Crop area for attachment name (center of the image)
        attachment_name_text = extract_text(image_path, crop_area=crop_area_name, save_crop=True, crop_name="name", failed_folder=failed_folder).strip()
        print(f"Attachment name text: {attachment_name_text}")

        # Clean attachment type and name to remove unexpected characters
        attachment_type = re.sub(r'[^\w\s-]', '', attachment_type_text)
        attachment_name = re.sub(r'[^\w\s-]', '', attachment_name_text)

        return attachment_type, attachment_name
    except Exception as e:
        print(f"Error identifying attachment in {image_path}: {e}")
        return None, None

# Function to process each weapon folder
def process_weapon_folder(weapon_folder):
    failed_folder = os.path.join(weapon_folder, "failed")
    os.makedirs(failed_folder, exist_ok=True)

    for root, dirs, files in os.walk(weapon_folder):
        for file in files:
            file_path = os.path.join(root, file)
            
            # Skip images inside attachment type folders
            relative_path = os.path.relpath(file_path, weapon_folder)
            if os.path.dirname(relative_path) and "failed" not in os.path.dirname(relative_path):  # Skip subdirectory files except "failed" folder
                continue

            try:
                text = extract_text(file_path)
                if "NO MODIFICATIONS" in text:
                    # Move the image to a base folder and rename to base.png
                    base_folder = os.path.join(weapon_folder, "base")
                    os.makedirs(base_folder, exist_ok=True)
                    new_name = "base.png"
                    new_path = os.path.join(base_folder, new_name)
                    os.replace(file_path, new_path)  # Use os.replace to overwrite existing files
                    print(f"Moved to {new_path}")
                else:
                    # Identify attachment type and name
                    attachment_type, attachment_name = identify_attachment(file_path, failed_folder)
                    
                    if attachment_type and attachment_name:
                        attachment_folder = os.path.join(weapon_folder, attachment_type)
                        os.makedirs(attachment_folder, exist_ok=True)
                        new_name = f"{attachment_name}.png"
                        new_path = os.path.join(attachment_folder, new_name)
                        os.replace(file_path, new_path)  # Use os.replace to overwrite existing files
                        print(f"Moved {file} to {new_path}")
                    else:
                        if not attachment_name:
                            # Save the cropped image for debugging purposes
                            extract_text(file_path, crop_area=crop_area_name, save_crop=True, crop_name=f"failed_name_{os.path.basename(file_path)}", failed_folder=failed_folder)
                        # Move the failed image to the failed folder
                        failed_image_path = os.path.join(failed_folder, os.path.basename(file_path))
                        os.replace(file_path, failed_image_path)
                        print(f"Failed to identify attachment type or name for {file}, moved to {failed_image_path}")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

# Process each game folder
for game_folder in os.listdir(base_dir):
    game_folder_path = os.path.join(base_dir, game_folder)
    if os.path.isdir(game_folder_path):
        for weapon_type_folder in os.listdir(game_folder_path):
            weapon_type_folder_path = os.path.join(game_folder_path, weapon_type_folder)
            if os.path.isdir(weapon_type_folder_path):
                for weapon_folder in os.listdir(weapon_type_folder_path):
                    weapon_folder_path = os.path.join(weapon_type_folder_path, weapon_folder)
                    if os.path.isdir(weapon_folder_path):
                        process_weapon_folder(weapon_folder_path)
