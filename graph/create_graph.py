import json
from pathlib import Path

# Get project folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Path to JSON file
json_file = BASE_DIR / "data" / "equipment.json"

# Read JSON
with open(json_file, "r") as file:
    data = json.load(file)

print(data)