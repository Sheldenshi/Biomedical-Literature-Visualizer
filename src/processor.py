import json
import os
from pathlib import Path

input_path = (
     Path.cwd()
     /".."
     /"output"
)

paths = list(input_path.glob('*.json'))
print(paths)
output_file = open('../hashmap.json', 'w')
labels = {}

for file in paths:
	data = json.load(open(file))
	print("Doing {}".format(file))
	for paper_id, paper in data.items():
		for sentence in paper:
			for i in range(len(sentence[1])):
				entity = sentence[1][i][0]
				label = sentence[1][i][1]
				if not entity in labels:
					labels[entity] = [label, paper_id]


json.dump(labels, output_file)
