import os
import shutil
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.vgg16 import preprocess_input

# Function to split data into train and test directories
def split_data(src_dir, train_class_dir, test_class_dir, test_size=0.2):
    # List all images in the source directory (subdirectories of rabbit/ and antelope/)
    all_images = [os.path.join(src_dir, f) for f in os.listdir(src_dir) if f.endswith('.jpg') or f.endswith('.png')]
    
    # Split data into train and test
    train_files, test_files = train_test_split(all_images, test_size=test_size, random_state=42)
    
    # Create target directories if they do not exist
    os.makedirs(train_class_dir, exist_ok=True)
    os.makedirs(test_class_dir, exist_ok=True)
    
    # Move the images to their respective directories
    for file in train_files:
        # Ensure the destination directory exists
        dest_path = os.path.join(train_class_dir, os.path.basename(file))
        shutil.move(file, dest_path)
        print(f"Moved {file} to {dest_path}")
    
    for file in test_files:
        # Ensure the destination directory exists
        dest_path = os.path.join(test_class_dir, os.path.basename(file))
        shutil.move(file, dest_path)
        print(f"Moved {file} to {dest_path}")

# Example usage for splitting the 'antelope' class
dataset_dir = 'images'  # Path to the source directory (images/antelope and images/rabbit)
train_dir = 'images/train'  # Path to the training directory
test_dir = 'images/test'  # Path to the testing directory

# Split the images of the antelope and rabbit classes into train/test
split_data(os.path.join(dataset_dir, 'antelope'), os.path.join(train_dir, 'antelope'), os.path.join(test_dir, 'antelope'))
split_data(os.path.join(dataset_dir, 'rabbit'), os.path.join(train_dir, 'rabbit'), os.path.join(test_dir, 'rabbit'))


# Function to resize and preprocess images for saving
def resize_and_preprocess_images(src_dir, dest_dir, target_size=(224, 224)):
    # Create the destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)
    
    # Iterate through all subdirectories (classes)
    for class_name in os.listdir(src_dir):
        class_dir = os.path.join(src_dir, class_name)
        if os.path.isdir(class_dir):
            class_dest_dir = os.path.join(dest_dir, class_name)
            os.makedirs(class_dest_dir, exist_ok=True)
            
            # Iterate through all files in the class directory
            for filename in os.listdir(class_dir):
                file_path = os.path.join(class_dir, filename)
                if filename.endswith('.jpg') or filename.endswith('.png'):
                    try:
                        # Open and resize the image
                        img = image.load_img(file_path, target_size=target_size)
                        img_array = image.img_to_array(img)  # Convert image to array

                        # Apply VGG preprocessing (mean subtraction, etc.)
                        img_array = preprocess_input(img_array)  # VGG-specific normalization

                        # Convert the image array back to a form that can be saved (rescale to 0-255)
                        img_array = img_array - np.min(img_array)  # Ensure that values are >=0
                        img_array = np.clip(img_array, 0, 255)  # Clip values to [0, 255]
                        img_array = img_array.astype(np.uint8)  # Convert to uint8 for saving

                        # Save the processed image
                        dest_path = os.path.join(class_dest_dir, filename)
                        image.save_img(dest_path, img_array)

                        print(f"Processed and saved: {filename}")
                    except Exception as e:
                        print(f"Error processing {filename}: {e}")

# Example usage for resizing and preprocessing both training and test images
resize_and_preprocess_images('images/train', 'images/resized_train')
resize_and_preprocess_images('images/test', 'images/resized_test')

print("Resizing, preprocessing, and saving images complete!")
