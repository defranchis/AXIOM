import os
import re

# Define the directory containing the folders
directory = 'data/'

# Define the pattern to match the folder names
pattern = re.compile(r'(Strip_C_300141_)200um(_m20C_\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}s)')

# Loop through each folder in the directory
for folder_name in os.listdir(directory):
    # Check if the folder name matches the pattern
    match = pattern.match(folder_name)
    if match:
        # Create the new folder name
        new_folder_name = match.group(1) + '120um' + match.group(2)
        # Rename the folder
        os.rename(os.path.join(directory, folder_name), os.path.join(directory, new_folder_name))

print("Folders renamed successfully!")
