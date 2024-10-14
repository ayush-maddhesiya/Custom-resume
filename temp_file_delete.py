import os

# Define the extensions of temporary files to delete
extensions_to_delete = ['.aux', '.log', '.out', '.pdf']

# Get the current working directory
current_directory = os.getcwd()

# Loop through the files in the current directory
for filename in os.listdir(current_directory):
    # Check if the file has one of the specified extensions
    if any(filename.endswith(ext) for ext in extensions_to_delete):
        file_path = os.path.join(current_directory, filename)
        try:
            if os.path.isfile(file_path):  # Check if it's a file
                os.remove(file_path)  # Remove file
                print(f"Deleted file: {file_path}")
            elif os.path.isdir(file_path):  # Check if it's a directory
                shutil.rmtree(file_path)  # Remove directory and all its contents
                print(f"Deleted directory: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

print("All specified temporary files and directories have been deleted.")
