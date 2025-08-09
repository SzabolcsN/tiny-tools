import os

def list_all_directories(path, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        for root, dirs, files in os.walk(path):
            for d in dirs:
                full_path = os.path.join(root, d)
                f.write(full_path + "\n")

path = "C:\\"
output_file = "directories.txt"

list_all_directories(path, output_file)
print(f"Directory list saved to {output_file}")
