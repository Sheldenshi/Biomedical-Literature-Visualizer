import json
import os
from py2neo import Graph, Node, Relationship
from itertools import combinations 
from pathlib import Path
import time

uri = "bolt://localhost:7687"
user = "neo4j"
password = "your password"

g = Graph(uri=uri, user=user, password=password)

# optionally clear the graph
g.delete_all()

# begin a transaction
tx = g.begin()


input_path = (
     Path.cwd()
     /"output"
)

paths = list(input_path.glob('*.json'))

hashmap_file = open('hashmap.json')
hashmap = json.load(hashmap_file)

def add_nodes(word_lable_pairs, label_to_graph):
	counter = 0
	for key, value in word_lable_pairs.items():
		if value == label_to_graph:
			tx.create(Node(value, name=key))
			counter += 1
		if counter == 500:
			#tx.commit()
			#print("Commit {} nodes".format(counter))
			#time.sleep(5)
			counter = 0
	#tx.commit()
	#time.sleep(2)


def add_to_graph():
	for i in range(len(result)):
		tx.create(Node(labels[result[i][0]], name=result[i][0]))
	

	statement_1 = "MATCH (a {name:$A}), (b {name:$B}) CREATE (a)-[:Link]->(b)"
	
	for n1, n2 in result:
		tx.run(statement_1, {"A": n1, "B": n2})

	tx.commit()

def add_relations(word_word_pairs):
	statement = "MATCH (a {name:$A}), (b {name:$B}) CREATE (a)-[:Link]->(b)"
	for n1, n2 in word_word_pairs:
		tx.run(statement, {"A": n1, "B": n2})
	



def graph_label(label_to_graph):
	add_nodes(hashmap, label_to_graph)

	for file in paths:
		print("Connecting {}".format(file))
		all_pairs = []
		seen = set()
		data = json.load(open(file))
		for paper in list(data.values()):
			for sentence in paper:
				entities = []
				for i in range(len(sentence[1])):
					entity = sentence[1][i][0]
					label = sentence[1][i][1]
					if label_to_graph == label and entity not in seen:
						seen.add(entity)
						entities.append(entity)
					
					
				#entities = [i[0] for i in sentence[1]]

				all_pairs.extend(list(combinations(entities, 2)))
		add_relations(all_pairs)
	tx.commit()


graph_label("DNA")