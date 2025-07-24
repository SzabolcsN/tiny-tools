import re
import os

input_file = os.path.join(os.path.dirname(__file__), 'data.txt')

with open(input_file, 'r', encoding='utf-8') as f:
    data = f.read()

functions = [match.strip().strip('"') for match in re.findall(r'= (.+)$', data, re.MULTILINE)]

result = ', '.join(functions)

output_file = os.path.join(os.path.dirname(__file__), 'functions.txt')

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(result)

print(f"Saved {len(functions)} to {output_file}")
