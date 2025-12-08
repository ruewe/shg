import csv
import json

csv_path = "Pflanzplan_2025.csv"
json_path = "Pflanzplan_2025.json"
def csv_to_json(csv_path, json_path, delimiter=","):
    data = []

    with open(csv_path, "r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=delimiter)
        for row in reader:
            data.append(row)

    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)

# Beispielaufruf
csv_to_json(csv_path=csv_path, json_path=json_path, delimiter=",")

import io, os
p = json_path
with io.open(p, "r", encoding="utf-8") as f:
    s = f.read().replace("\ufeff", "")
    s = s.replace("🥕 ", "")
with io.open(p, "w", encoding="utf-8") as f:
    f.write(s)
print("BOM entfernt:", p)
