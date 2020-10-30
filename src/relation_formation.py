import json
import os
from py2neo import Graph, Node, Relationship
from itertools import combinations 
from pathlib import Path
import time

#uri = "neo4j://localhost:7687"
uri = "bolt://10.0.1.4:7687"
user = "neo4j"
password = "X7ZWbpV{7j}T]b"

g = Graph(uri, user=user, password=password)

# optionally clear the graph
#g.delete_all()

# begin a transaction
tx = g.begin()


input_path = (
     Path.cwd()
     /"../output"
)

paths = list(input_path.glob('*.json'))

hashmap_file = open('../hashmap.json')
print("open json")
#hashmap_file = open('hashmap.json')
hashmap = json.load(hashmap_file)
print("load json")

def add_nodes(word_label_paper_map, label_to_graph):
	global tx
	for word, pairs in word_label_paper_map.items():
		if pairs[0] == label_to_graph:
			tx.create(Node(pairs[0], name=word, paper_id=pairs[1]))
	tx.commit()
	tx = g.begin()

def add_to_graph():
	for i in range(len(result)):
		tx.create(Node(labels[result[i][0]], name=result[i][0]))
	

	statement_1 = "MATCH (a {name:$A}), (b {name:$B}) CREATE (a)-[:Link]->(b)"
	
	for n1, n2 in result:
		tx.run(statement_1, {"A": n1, "B": n2})

	tx.commit()

def add_relations(word_word_pairs):
	global tx
	statement = "MATCH (a {name:$A}), (b {name:$B}) CREATE (a)-[:Link]->(b)"
	for n1, n2 in word_word_pairs:
		tx.run(statement, {"A": n1, "B": n2})
	tx.commit()
	tx = g.begin()
	



def graph_label(labels_to_graph):
	for label in labels_to_graph:
		
		
		print(f'Adding label: {label}')
		add_nodes(hashmap, label)

		

	for file in paths:
		print(f"Connecting {label} in {file}")
		all_pairs = []
		seen = set()
		data = json.load(open(file))
		for paper_id, paper in data.items():
			for sentence in paper:
				entities = []
				for i in range(len(sentence[1])):
					entity = sentence[1][i][0]
					pair_label = sentence[1][i][1]
					if pair_label in labels_to_graph and entity not in seen:
						seen.add(entity)
						entities.append(entity)
					
					
				#entities = [i[0] for i in sentence[1]]

				all_pairs.extend(list(combinations(entities, 2)))
		add_relations(all_pairs)
	tx.commit()


graph_label(["DNA", "DISEASE", "ORGANISM"])