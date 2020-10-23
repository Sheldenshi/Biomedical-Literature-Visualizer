import json
import os
from pathlib import Path

input_path = (
     Path.cwd()
     /"output"
)

paths = list(input_path.glob('*.json'))

output_file = open('hashmap.json', 'w')
labels = {}

for file in paths:
	data = json.load(open(file))
	print("Doing {}".format(file))
	for paper in list(data.values()):
		for sentence in paper:
			for i in range(len(sentence[1])):
				entity = sentence[1][i][0]
				label = sentence[1][i][1]
				if not entity in labels:
					labels[entity] = label


json.dump(labels, output_file)
