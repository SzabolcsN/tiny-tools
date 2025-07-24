import os
from pydub import AudioSegment

INPUT_FOLDER = "./sounds"
OUTPUT_FOLDER = "quieted"
REDUCE_DB = 10

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def reduce_volume(input_path, output_path, reduce_db):
    audio = AudioSegment.from_wav(input_path)
    quieter_audio = audio - reduce_db
    quieter_audio.export(output_path, format="wav")
    print(f"Reduced: {input_path} -> {output_path}")

for filename in os.listdir(INPUT_FOLDER):
    if filename.lower().endswith(".wav"):
        input_file = os.path.join(INPUT_FOLDER, filename)
        output_file = os.path.join(OUTPUT_FOLDER, filename)
        reduce_volume(input_file, output_file, REDUCE_DB)

print("Success")
