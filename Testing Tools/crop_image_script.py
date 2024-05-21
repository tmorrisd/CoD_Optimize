import os
from PIL import Image

def crop_image(input_path, output_path, left, top, right, bottom):
    # Load the image
    img = Image.open(input_path)

    # Crop the image
    cropped_img = img.crop((left, top, right, bottom))

    # Save the cropped image
    cropped_img.save(output_path)

def process_folder(folder_path, left, top, right, bottom):
    if not os.path.exists(folder_path):
        print(f"The folder path {folder_path} does not exist. Please check the path and try again.")
        parent_folder = os.path.dirname(folder_path)
        print(f"Contents of the parent directory ({parent_folder}):")
        print(os.listdir(parent_folder))
        return

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):  # Add any other image formats if necessary
            input_path = os.path.join(folder_path, filename)
            output_path = os.path.join(folder_path, f"cropped_{filename}")
            print(f"Processing {input_path}")
            crop_image(input_path, output_path, left, top, right, bottom)

if __name__ == "__main__":
    folder_path = r"C:\Users\Tyler\CoDDev\CoD_Optimize\Images\MW3\Assualt Rifles\BP50"  # Corrected path
    left = 175 # Update with your coordinates
    top = 65   # Update with your coordinates
    right = 350  # Update with your coordinates
    bottom = 110  # Update with your coordinates

    process_folder(folder_path, left, top, right, bottom)
