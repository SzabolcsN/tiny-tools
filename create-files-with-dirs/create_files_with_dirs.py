import os
import random

def create_files_in_directories(base_directory, number_of_files, size_range, files_per_directory):
    if not os.path.exists(base_directory):
        os.makedirs(base_directory)

    for i in range(number_of_files):
        directory_index = (i // files_per_directory) + 1
        subdirectory = os.path.join(base_directory, str(directory_index))

        if not os.path.exists(subdirectory):
            os.makedirs(subdirectory)

        file_name = f"file_{i + 1}.txt"
        file_path = os.path.join(subdirectory, file_name)

        file_size = random.randint(size_range[0], size_range[1])

        with open(file_path, 'wb') as f:
            f.write(os.urandom(file_size))

        print(f"Created file {i + 1}/{number_of_files}")

    print(f"{number_of_files} files created in '{base_directory}' ({files_per_directory} / dir)")

base_directory = "C:\\"
number_of_files = 3000
size_range = (1024, 10240)
files_per_directory = 50

create_files_in_directories(base_directory, number_of_files, size_range, files_per_directory)