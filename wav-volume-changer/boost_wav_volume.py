import os
from pydub import AudioSegment

INPUT_FOLDER = "./sounds"
OUTPUT_FOLDER = "boosted"
BOOST_DB = 10

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def boost_volume(input_path, output_path, boost_db):
    audio = AudioSegment.from_wav(input_path)
    louder_audio = audio + boost_db
    louder_audio.export(output_path, format="wav")
    print(f"Boosted: {input_path} -> {output_path}")

for filename in os.listdir(INPUT_FOLDER):
    if filename.lower().endswith(".wav"):
        input_file = os.path.join(INPUT_FOLDER, filename)
        output_file = os.path.join(OUTPUT_FOLDER, filename)
        boost_volume(input_file, output_file, BOOST_DB)

print("Success")
